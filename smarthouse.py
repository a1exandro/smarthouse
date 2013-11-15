# smarthouse by a1ex! <dok-alex@mail.ru>

__author__ = 'a1ex!'
__version__ = '1.0'

mod_dir = "controllers"
hndl_dir = "handlers"

from engine import system
import sys

def main():
    sys.path.append('engine')
    cfg = {'mod_dir':mod_dir,'hndl_dir':hndl_dir,'cfg_path':'config.cfg','version':__version__}
    engn = system.TSystem(cfg)
    engn.init()
    print('bye bye')

if __name__ == '__main__':
    main()