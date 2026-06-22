# ==============================================================================
#   PLC operation components
# ------------------------------------------------------------------------------
#  Copyright (C) Organisation europeenne pour la Recherche nucleaire (CERN)
#  All rights reserved.
# 
#   \author   Markus Frank
#   \date     2018-12-18
#   \version  1.0
# 
# ==============================================================================
__version__ = "1.0"
__author__  = "Markus Frank <Markus.Frank@cern.ch>"

import os
import sys
import errno

global SKETCHES
global TEMPLATE_DIR
global PROJECTS_DIR

HOME = os.environ['HOME']
SKETCHES = HOME + os.sep + 'Arduino/sketches'
TEMPLATE_DIR = os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0]
PROJECTS_DIR = HOME + os.sep + 'Documents/PlatformIO/Projects'

# ==============================================================================
def log(msg):
  print(msg)

# ==============================================================================
def execute(command, msg='Execute command'):
  ret = os.system(command)
  log( '+++ %-32s %d %s'%(msg, ret, command, ) )
  if ret != 0:
    log( f'+++ ERROR command execution failed [{os.strerror(ret)}].' )
    raise(Exception(os.strerror(ret)))
  return ret

# ==============================================================================
class Project:
  # ============================================================================
  def __init__(self, source_path):
    p = os.path.split(source_path)
    self.name = p[1]
    self.directory = p[0]
    p = os.path.split(self.directory)
    self.name = p[1] + os.sep + self.name
    self.source = source_path
    self.project_dir = None

  # ============================================================================
  def project_directory(self):
    pdir = PROJECTS_DIR+os.sep+self.name
    return pdir
  
  # ============================================================================
  def copy_dir(self, from_dir, to_dir):
    return execute('cp -r '+from_dir+' '+to_dir)

  # ============================================================================
  def from_template(self, template):
    self.project_dir = self.project_directory()

    if not os.path.exists(template):
      log( f'+++ ERROR: Directory containing template {template} does not exists.' )
      raise(FileNotFoundError(template))

    if os.path.exists(self.project_dir):
      log( f'+++ ERROR: Directory {self.project_dir} already exists. No project created.' )
      raise(FileExistsError(self.project_dir))

    sub_dirs = self.project_dir.split(os.sep)
    d = ''
    for sd in sub_dirs[:-1]:
      d = d + os.sep + sd
      if not os.path.exists(d):
        print( f' ----> {d} ' )
        os.mkdir(d)
      
    ret = self.copy_dir(template, self.project_dir)
    if ret:
      log( f'+++ ERROR: Failed to copy directory {template} to {self.project_dir} [{os.strerror(ret)}]' )
      raise(ret)

    os.chdir(self.project_dir)  # Throws already FileNotFoundError
    os.symlink( self.source, 'src', target_is_directory=True )
    return 0  

  # ============================================================================
  def show_vscode_command(self):
    log( f'+++ To start the vs-code project "{self.name}" in {self.source} type:' )
    log( f' code {self.project_dir}'  )


# ==============================================================================
def create_project(source_path, args):
  sources = os.path.abspath(source_path)
  from_dir = TEMPLATE_DIR
  if not os.path.exists(source_path):
    log( f"+++ No project '{sources}' found [{os.strerror(errno.ENOENT)}]" )
    sources = (os.getcwd() + os.sep + source_path).replace('//','/')
    sources = os.path.abspath(sources)
     
  if not os.path.exists(source_path):
    log( f"+++ No project '{sources}' found [{os.strerror(errno.ENOENT)}]" )
    sources = (SKETCHES + os.sep + source_path).replace('//','/')
    sources = os.path.abspath(sources)

  if not os.path.exists(sources):
    log( f"+++ No project '{sources}' found [{os.strerror(errno.ENOENT)}]" )
    sys.exit(errno.EINVAL)

  log( f"+++ Using project directory '{sources}'." )
  project = None
  try:
    project = Project(sources)
    project_directory = project.project_directory()
    if args.recreate_project and os.path.exists(project_directory):
      execute( f'rm -rf {project_directory}', 'Cleanup project directory')
    elif args.remove_project:
      ret = execute( f'rm -rf {project_directory}', 'Cleanup project directory')
      sys.exit(ret)
    project.from_template(from_dir)
  except Exception as exc:
    log( f"+++ ERROR: {str(exc)} " )
  return project


# ==============================================================================
def run():
  import pathlib
  import argparse
  global SKETCHES
  global TEMPLATE_DIR
  global PROJECTS_DIR
  
  parser = argparse.ArgumentParser(
    allow_abbrev = True,
    description  = 'PlatformIO project generator',
    epilog       = '                          M.Frank' )

  parser.add_argument(
    '-p',
    '--project',
    type = pathlib.Path,
    dest = 'project_path',
    default = None,
    help = 'Path to source project',
   )

  parser.add_argument(
    '-c',
    '--code',
    action = 'store_true',
    dest = 'start_vscode',
    default = False,
    help = 'Start Visual Code project',
  )

  parser.add_argument(
    '-r',
    '--recreate',
    action = 'store_true',
    dest = 'recreate_project',
    default = False,
    help = 'Recreate Visual Code project',
  )

  parser.add_argument(
    '-R',
    '--remode',
    action = 'store_true',
    dest = 'remove_project',
    default = False,
    help = 'Remove Visual Code project without recreating',
  )

  parser.add_argument(
    '-s',
    '--sketches-dir',
    type = pathlib.Path,
    dest = 'sketches_dir',
    default = ''+SKETCHES,
    help = 'Arduino sketches directory Default: '+SKETCHES
  )

  parser.add_argument(
    '-t',
    '--template-dir',
    type = pathlib.Path,
    dest = 'template_dir',
    default = ''+TEMPLATE_DIR,
    help = 'PlatformIO template directory. Default: '+TEMPLATE_DIR
  )

  parser.add_argument(
    '-P',
    '--projects-dir',
    type = str,
    dest = 'projects_dir',
    default = ''+PROJECTS_DIR,
    help = 'Location to place PlatformIO projects. Default: '+PROJECTS_DIR
  )

  args = parser.parse_args()
  project = None
  if len(sys.argv) == 2:
    project = create_project(sys.argv[1])
  else:
    SKETCHES     = str(args.sketches_dir)
    TEMPLATE_DIR = str(args.template_dir)
    PROJECTS_DIR = str(args.projects_dir)
    print( f'+++ SKETCHES:     {SKETCHES} ')
    print( f'+++ TEMPLATE_DIR: {TEMPLATE_DIR} ')
    print( f'+++ PROJECTS_DIR: {PROJECTS_DIR} ')
    project = create_project(str(args.project_path), args)
  if project:
    if args.start_vscode:
      execute( f'code {project.project_directory()} &' )
    else:
      project.show_vscode_command()

    sys.exit(0)
  sys.exit(errno.EINVAL)
