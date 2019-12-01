import pandas as pd
import climvis
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Select, Div
from bokeh.models.widgets.inputs import AutocompleteInput
from bokeh.layouts import column, row
from bokeh.plotting import figure


def get_lat_lon(city):
    df = pd.read_csv(climvis.cfg.world_cities)
    lat = df.loc[df.Name == city].Lat.values[0]
    lon = df.loc[df.Name == city].Lon.values[0]
    return(lat, lon)


def resample_data(df, method, variable):
    # Specifying the month when summer starts.
    start_month = '04'
    methods = {'Yearly': ['12M', '01', 0, 1],
               'Summer': ['6M', start_month, 0, 2],
               'Winter': ['6M', start_month, 1, 2]}
    use_method = methods[method]
    if variable == 'Precipitaiton':
        data = df['1901-'+use_method[1]:].resample(use_method[0],
                                                   closed='left').sum()
    else:
        data = df['1901-'+use_method[1]:].resample(use_method[0],
                                                   closed='left').mean()
    return(data[use_method[2]::use_method[3]])


def get_data(city, variable, method):
    lat, lon = get_lat_lon(city)
    df = climvis.core.get_cru_timeseries(lon, lat)
    data = resample_data(df, method, variable)
    return(ColumnDataSource(data=data))


def create_plot(source_1, source_2, title, variable):
    y_labels = {'Precipitation': 'Precipitation [mm]',
                'Temperature': 'Temperature [°C]'}
    plot = figure(x_axis_type="datetime", plot_width=1000)
    plot.title.text = title
    plot.line('time', variable_list[variable], source=source_1,
              legend_label=city_1, line_width=1.5)
    plot.line('time', variable_list[variable], source=source_2,
              color='forestgreen', legend_label=city_2, line_width=1.5)
    plot.yaxis.axis_label = y_labels[variable]
    plot.legend.location = 'top_left'
    # Not implemented in line plots yet.
    # plot.legend.click_policy = 'mute'
    return(plot)


def update_plot(attrname, old, new):
    # Get the new value of city and variable.
    global city_1, city_2
    city_1 = city_1_select.value
    city_2 = city_2_select.value
    variable = variable_select.value
    method = method_select.value
    title = method + ' ' + variable.lower() + ' data in ' + city_1 + ' and '
    + city_2 + '.'

    src_1 = get_data(city_1, variable, method)
    src_2 = get_data(city_2, variable, method)
    layout.children[1] = create_plot(src_1, src_2, title, variable)


city_1 = 'Innsbruck'
city_2 = 'Goteborg'
variable = 'Temperature'
method = 'Yearly'
# cities_list = ['Innsbruck', 'Goteborg', 'Zurich', 'Sydney']
# These are not stirngs yet.
cities = pd.read_csv(climvis.cfg.world_cities, usecols=['Name'])
cities_list = cities['Name'].dropna().tolist()

variable_list = {'Temperature': 'tmp', 'Precipitation': 'pre'}
methods_list = ['Yearly', 'Summer', 'Winter']
# city_1_select = Select(value=city_1, title='City 1', options=cities_list)
# city_2_select = Select(value=city_2, title='City 2', options=cities_list)
city_1_title = 'Search for the first city'
city_2_title = 'Seatch for the second city'
city_1_select = AutocompleteInput(value=city_1, completions=cities_list,
                                  min_characters=3, title=city_1_title)
city_2_select = AutocompleteInput(value=city_2, completions=cities_list,
                                  min_characters=3, title=city_2_title)
variable_select = Select(value=variable, title='Variable',
                         options=list(variable_list.keys()))
method_select = Select(value=method, title='Period', options=methods_list)

source_1 = get_data(city_1, variable, method)
source_2 = get_data(city_2, variable, method)
title = (method + ' ' + variable.lower() + ' in ' + city_1 + ' and ' + city_2
         + '.')
plot = create_plot(source_1, source_2, title, variable)

for w in [city_1_select, city_2_select, variable_select, method_select]:
    w.on_change('value', update_plot)

text = ('<font size="5">Welcome to the ClimTrend visulaization tool.'
        ' Compare the climate in two cities by using the fields'
        ' below.</font>')
p = Div(text=text, width=300, height=200)
controls = column(p, city_1_select, city_2_select, variable_select,
                  method_select)
layout = row(controls, plot)
curdoc().add_root(layout)
curdoc().title = 'Test'
