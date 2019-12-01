import pandas as pd
import climvis
from tornado.ioloop import IOLoop
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.server.server import Server
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Select, Div
from bokeh.models.widgets.inputs import AutocompleteInput
from bokeh.layouts import column, row
from bokeh.plotting import figure


def get_lat_lon(city):
    """Return the latitude and longitude of a city available in the
    world_cities csv file.

    Paramters
    ---------
    city : String
        Name of the city.

    Returns
    -------
    Latitude and longitude of the city.
    """
    df = pd.read_csv(climvis.cfg.world_cities)
    # Find lat and lon of city in dataframe.
    lat = df.loc[df.Name == city].Lat.values[0]
    lon = df.loc[df.Name == city].Lon.values[0]
    return(lat, lon)


def resample_data(df, method, variable, lat):
    """Resamples a pandas dataframe containing monthly averages of a climate
    variable.

    Parameters
    ----------
    df : Pandas DataFrame
        DataFrame containing the data to be resampled.
    method : String
        String describing which method to use for resampling.
    variable : String
        String describing what climatic variable the dataframe contains.
    lat : float
        Latitude of the gridpoint.

    Returns
    -------
    The resampled dataframe.
    """
    # Specifying the month when seasons change.
    start_month = '04'
    # Southern hemisphere winter/summer has to be reversed. Maybe there is an
    # prettier way?
    if lat < 0 and method == 'Summer':
        method = 'Winter'
    elif lat < 0 and method == 'Winter':
        method = 'Summer'
    # Dict of the different resampling methods.
    methods = {'Yearly': ['12M', '01', 0, 1],
               'Summer': ['6M', start_month, 0, 2],
               'Winter': ['6M', start_month, 1, 2]}
    use_method = methods[method]
    # For precipitation monthly means should be summed.
    if variable == 'Precipitation':
        data = df['1901-'+use_method[1]:].resample(use_method[0],
                                                   closed='left').sum()
    # For temperature an average should be calculated for the monthly means.
    else:
        data = df['1901-'+use_method[1]:].resample(use_method[0],
                                                   closed='left').mean()
    return(data[use_method[2]::use_method[3]])


def get_data(city, variable, method):
    """Get the data for a specified city.

    Parameters
    ----------
    city : String
        Name of city to retreive data from.
    variable : String
        Name of climatic variable to retreive.
    method : String
        Name of resampling method.

    Returns
    -------
    The requested data as a ColumnDataSource.
    """
    # Fetch the latitude and longitude of the specified city.
    lat, lon = get_lat_lon(city)
    # The CRU timeseries for the gridpoint.
    df = climvis.core.get_cru_timeseries(lon, lat)
    # Resample the CRU data based on requested method.
    data = resample_data(df, method, variable, lat)
    return(ColumnDataSource(data=data))


def create_plot(source_1, source_2, title, variable):
    """Create a bokeh line plot from two data sources.

    Parameters
    ----------
    source_1 : ColumnDataSource
        Data source for the first line plot.
    source_2 : ColumnDataSource
        Data source for the second line plot.
    title : String
        Title of the plot.
    variable : String
        The variable available in source_1 and source_2 to plot. Makes use of
        the variable dictionary.
    """
    y_labels = {'Precipitation': 'Precipitation [mm]',
                'Temperature': 'Temperature [°C]'}
    plot = figure(x_axis_type="datetime", plot_width=1000)
    plot.title.text = title
    # Plot the the selected variable. Maybe this should be done in get_data
    # instead?
    plot.line('time', variable_dict[variable], source=source_1,
              legend_label=city_1, line_width=1.5)
    plot.line('time', variable_dict[variable], source=source_2,
              color='forestgreen', legend_label=city_2, line_width=1.5)
    plot.yaxis.axis_label = y_labels[variable]
    plot.legend.location = 'top_left'
    # Not implemented in line plots yet.
    # plot.legend.click_policy = 'mute'
    return(plot)


# Initialization
city_1 = 'Innsbruck'
city_2 = 'Goteborg'
variable = 'Temperature'
method = 'Yearly'
# Read all city names in word_cities and create list based on these.
cities = pd.read_csv(climvis.cfg.world_cities, usecols=['Name'])
# Have to drop the NaN values for bokeh widget to accept the list.
cities_list = cities['Name'].dropna().tolist()

variable_dict = {'Temperature': 'tmp', 'Precipitation': 'pre'}
methods_list = ['Yearly', 'Summer', 'Winter']


def modify_doc(doc):
    """Create and modify the bokeh document. Later ran by the tornado
    server."""
    city_1_title = 'Search for the first city'
    city_2_title = 'Search for the second city'
    # Adding selectors, essentially the controls, to the app.
    city_1_select = AutocompleteInput(value=city_1, completions=cities_list,
                                      min_characters=3, title=city_1_title)
    city_2_select = AutocompleteInput(value=city_2, completions=cities_list,
                                      min_characters=3, title=city_2_title)
    variable_select = Select(value=variable, title='Variable',
                             options=list(variable_dict.keys()))
    method_select = Select(value=method, title='Period', options=methods_list)
    # Initialize the app with some data.
    source_1 = get_data(city_1, variable, method)
    source_2 = get_data(city_2, variable, method)
    title = (method + ' ' + variable.lower() + ' in ' + city_1 + ' and '
             + city_2 + '.')
    plot = create_plot(source_1, source_2, title, variable)

    def update_plot(attrname, old, new):
        """This is called when any of the widgets are changed, updates the
        plot"""
        # Need to access the value of the global variables.
        global city_1, city_2
        # Get the new value of cities and variable.
        city_1 = city_1_select.value
        city_2 = city_2_select.value
        variable = variable_select.value
        method = method_select.value
        # Set new title of plot based on new variables.
        title = (method + ' ' + variable.lower() + ' data in ' + city_1 +
                 ' and ' + city_2 + '.')
        # Get new source data based on the new parameters.
        src_1 = get_data(city_1, variable, method)
        src_2 = get_data(city_2, variable, method)
        # This is what is actually updating the plot, the plot is the second
        # child of the layout.
        layout.children[1] = create_plot(src_1, src_2, title, variable)

    # Looping through all the selectors to detect changes.
    for w in [city_1_select, city_2_select, variable_select, method_select]:
        w.on_change('value', update_plot)

    text = ('<font size="5">Welcome to the ClimTrend visualization tool.'
            ' Compare the climate in two cities by using the controls'
            ' below.</font>')
    p = Div(text=text, width=300, height=200)
    controls = column(p, city_1_select, city_2_select, variable_select,
                      method_select)
    # Add the controls of the app and the plot to the first row of the layout.
    layout = row(controls, plot)
    doc.add_root(layout)
    doc.title = 'Test'


def launch_app(browser):
    """This is where the server is launched, and we connect to the server.
    Recipe from the bokeh reference pages."""
    io_loop = IOLoop.current()
    bokeh_app = Application(FunctionHandler(modify_doc))
    server = Server({"/": bokeh_app}, io_loop=io_loop)
    server.start()
    print('Opening ClimTrend on http://localhost:5006/')

    # This equivalent to running bokeh serve --show from the command line. Kind
    # of. Not good for deployment.
    io_loop.add_callback(server.show, "/")
    io_loop.start()


if __name__ == '__main__':
    launch_app()
