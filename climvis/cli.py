import webbrowser
import sys
import climvis
from climvis import bokeh_proto_2

HELP = """cruvis: CRU data visualization at a selected location.

Usage:
   -h, --help            : print the help
   -v, --version         : print the installed version
   -l, --loc [LON] [LAT] : the location at which the climate data must be
                           extracted
   --no-browser          : the default behavior is to open a browser with the
                           newly generated visualisation. Set to ignore
                           and print the path to the html file instead
"""


def cruvis_io(args):
    """The actual command line tool.

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    """

    if len(args) == 0:
        print(HELP)
    elif args[0] in ['-h', '--help']:
        print(HELP)
    elif args[0] in ['-v', '--version']:
        print('cruvis: ' + climvis.__version__)
        print('License: public domain')
        print('cruvis is provided "as is", without warranty of any kind')
    elif args[0] in ['-l', '--loc']:
        if len(args) < 3:
            print('cruvis --loc needs lon and lat parameters!')
            return
        lon, lat = float(args[1]), float(args[2])
        html_path = climvis.write_html(lon, lat)
        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab(html_path)
    else:
        print('cruvis: command not understood. '
              'Type "cruvis --help" for usage options.')


def cruvis():
    """Entry point for the cruvis application script"""

    # Minimal code because we don't want to test for sys.argv
    # (we could, but this is too complicated for now)
    cruvis_io(sys.argv[1:])


climTrendHelp = '''climTrend: bokeh app to compare the climate in two cities.
Run command without any arguments to launch the app.

Usage:
    -h, --help:     print the help.

'''


def climTrend_io(args):
    if len(args) != 0:
        if args[0] in ['-h', '--help']:
            print(climTrendHelp)
        elif len(args) > 1:
            print(climTrendHelp)
    else:
        bokeh_proto_2.launch_app()


def climTrend():
    """Entry point for the climTrend bokeh app"""
    climTrend_io(sys.argv[1:])
