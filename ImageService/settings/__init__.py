
env_name = 'dev'

if env_name == 'prod':
    from .prod import *
elif env_name == 'dev':
    from .dev import *