#!/bin/python3
# ==============================================================================
#   PLC operation components
# ------------------------------------------------------------------------------
#   Copyright (C) Organisation europeenne pour la Recherche nucleaire (CERN)
#   All rights reserved.
# 
#   \author   Markus Frank
#   \date     2025-12-18
#   \version  1.0
# 
# ==============================================================================
__version__ = "1.0"
__author__  = "Markus Frank <Markus.Frank@cern.ch>"

import os
import sys
import errno
#import pio

if __name__ == '__main__':
  appended = 0
  dir_name = os.path.split(os.path.split(__file__)[0])[0]
  if str(sys.path).find("['"+dir_name+"']") < 0:
    sys.path.append(dir_name)
    appended = 1
  import pio
  if appended:
    pio.log( f'Appended to PYTHONPATH: {dir_name}' )
  if len(sys.argv) == 1:
    pio.log( f'usage:   python {os.path.relpath(__file__)} <project-directory> ' )
    sys.exit(errno.EINVAL)
  ret = pio.run()
  sys.exit(ret)
