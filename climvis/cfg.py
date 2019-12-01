"""This configuration module is a container for parameters and constants."""
import os

# Read the path from the first line in the .cruvis.txt in home folder.
with open(os.path.expanduser('~/.cruvis.txt')) as f:
    cru_dir = f.readline().strip()

cru_tmp_file = cru_dir + 'cru_ts4.03.1901.2018.tmp.dat.nc'
cru_pre_file = cru_dir + 'cru_ts4.03.1901.2018.pre.dat.nc'
cru_topo_file = cru_dir + 'cru_cl1_topography.nc'
# Make sure that these files exist.
exists = [os.path.isfile(cru_tmp_file), os.path.isfile(cru_pre_file),
          os.path.isfile(cru_topo_file)]
if not all(exists):
    raise FileNotFoundError(
        'The CRU files are not available on this system. For cruvis to work'
        ' properly, please create a file called ".cruvis" in your HOME'
        ' directory, and indicate the path to the CRU directory in it.'
    )

bdir = os.path.dirname(__file__)
html_tpl = os.path.join(bdir, 'data', 'template.html')
world_cities = os.path.join(bdir, 'data', 'world_cities.csv')

default_zoom = 8
