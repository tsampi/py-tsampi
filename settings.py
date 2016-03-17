import os


def here(x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

os.environ['GNUPGHOME'] = here('keys')

TSAMPI_HOME = here('./repos/tsampidb-0')
TIMEOUT = 1
MY_KEY = None
