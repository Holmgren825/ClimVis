from climvis import bokeh_proto
import pytest
import numpy as np


def test_get_lat_lon():
    city = 'Innsbruck'
    city_2 = bokeh_proto.cities_list[1]
    lat_corr = 47.2666667
    lon_corr = 11.4
    lat, lon = bokeh_proto.get_lat_lon(city)
    lat2, lon2 = bokeh_proto.get_lat_lon(city_2)

    np.testing.assert_almost_equal(lat, lat_corr, decimal=4)
    np.testing.assert_almost_equal(lon, lon_corr, decimal=4)
    print(lat2, lon2)
