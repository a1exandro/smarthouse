__author__ = 'a1ex!'
__version__ = '1.0'

mod_dir = "controllers"
hndl_dir = "handlers"

import configparser

cfg = {'mod_dir':mod_dir,'hndl_dir':hndl_dir,'cfg_path':'config.cfg','version':__version__}

cfgParser = configparser.ConfigParser()
