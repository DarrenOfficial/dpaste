VERSION = (3, 1)

__version__ = '{major}.{minor}{rest}'.format(
    major=VERSION[0],
    minor=VERSION[1],
    rest=''.join(str(i) for i in VERSION[2:]),
)

default_app_config = 'dpaste.apps.dpasteAppConfig'
