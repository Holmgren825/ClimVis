"""Tests for climTrend.

Author: Erik Holmgren
"""
from climvis import climtrend
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import bokeh


def test_get_lat_lon():
    city = 'Innsbruck'
    city_2 = climtrend.cities_list[1]
    lat_corr = 47.2666667
    lon_corr = 11.4
    lat, lon = climtrend.get_lat_lon(city)
    lat2, lon2 = climtrend.get_lat_lon(city_2)

    np.testing.assert_almost_equal(lat, lat_corr, decimal=4)
    np.testing.assert_almost_equal(lon, lon_corr, decimal=4)


def test_resample_data():
    # Some dummy data.
    data = np.arange(24)
    index = pd.date_range('2017-01-01', periods=24,
                          freq='MS').tolist()
    df = pd.DataFrame(data, index)
    method = 'Yearly'
    variable = 'Temperature'
    lat = 15
    df_resample = climtrend.resample_data(df, method, variable, lat)
    # What the returned data is supposed to look like.
    index_corr = pd.date_range('2017-12-31', periods=2, freq='12M').tolist()
    data_corr = [data[:12].mean(), data[12:].mean()]
    df_corr = pd.DataFrame(data_corr, index_corr)
    pdt.assert_frame_equal(df_resample, df_corr)
    # Case using summer period.
    method = 'Summer'
    variable = 'Temperature'
    df_resample_summer = climtrend.resample_data(df, method, variable, lat)
    # Maybe this is a bit too lazy.
    df_corr_summer = df['2017-04':].resample('6M', closed='left').mean()[0::2]
    pdt.assert_frame_equal(df_resample_summer, df_corr_summer)
    # Case using winter period.
    method = 'Winter'
    variable = 'Temperature'
    df_resample_winter = climtrend.resample_data(df, method, variable, lat)
    df_corr_winter = df['2017-04':].resample('6M', closed='left').mean()[1::2]
    pdt.assert_frame_equal(df_resample_winter, df_corr_winter)


def test_get_data():
    city = 'Innsbruck'
    variable = 'Temperature'
    method = 'Summer'
    data = climtrend.get_data(city, variable, method)

    # This function is only a collection of other functions, hence only testing
    # if it actually returns a dataframe.
    assert type(data) is pd.core.frame.DataFrame


def test_get_trend():
    variable = 'Temperature'
    data = np.arange(24)
    index = pd.date_range('2017-01-01', periods=24,
                          freq='MS').tolist()
    df = pd.DataFrame(data, index, columns=['tmp'])
    df_trend = climtrend.get_trend(df, variable)

    assert type(df_trend) is pd.core.frame.DataFrame
    # Since data is increasing monotonously, the trend minus itself should be
    # zero.
    assert (df_trend.trend - df_trend.trend == 0).all()


def test_create_plot():
    city_1 = 'Innsbruck'
    city_2 = 'Goteborg'
    variable = 'Temperature'
    method = 'Yearly'
    trend = 'False'
    source_1 = climtrend.get_data(city_1, variable, method)
    source_2 = climtrend.get_data(city_2, variable, method)
    title = 'Just a test title'

    test_plot = climtrend.create_plot(source_1, source_2, title, variable,
                                      trend)
    # Test if the returned plot is actually a plot.
    assert type(test_plot) is bokeh.plotting.Figure
