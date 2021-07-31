#!/usr/bin/env python3
import os, sys, time, logging, argparse
from pathlib import Path
import halo, termcolor
import json

DBG = 1
OUTPUT_DIRECTORY  = os.getenv('VDM_CAPABILITY_OUTPUT_DIRECTORY', './output')
INSTALL_DIRECTORY = os.getenv('VDM_CAPABILITY_INSTALL_DIRECTORY', '~/.vdm/capability')

class TypeWriter:
    def __init__(self):
        pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()
        pass

    def start(self):
        print()
        pass

    def write(self, words:list, duration=20, color='white', bg_color=None, bold=False):
        attrs = ['bold'] if bold else []
        for word in words:
            word = termcolor.colored(word, color=color, on_color=bg_color, attrs=attrs)
            print(word, end='')
            time.sleep( duration * 1E-3 )
        pass

    def stop(self):
        print()
        pass

    pass

class WorkSpace:
    def __init__(self, p, *p_l, **kargs):
        self.wrk = Path(p, *p_l).expanduser().resolve()
        self.pwd = Path.cwd()
        if 'forceUpdate' in kargs.keys():
            self.forceUpdate = True
        else:
            self.forceUpdate = False
        pass
    
    def __enter__(self):
        if not Path(self.wrk).is_dir():
            if self.forceUpdate:
                Path(self.wrk).mkdir(mode=0o755, parents=True, exist_ok=True)
            else:
                return self.__exit__(*sys.exc_info())
        else:
            pass
        os.chdir(self.wrk)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        os.chdir(self.pwd)
        if exc_tb: pass
        pass
    pass

class SimpleBuildSystem:
    def __init__(self):
        self.output_dir = Path(OUTPUT_DIRECTORY).expanduser().resolve()
        self.install_dir = Path(INSTALL_DIRECTORY).expanduser().resolve()
        pass

    def _install_cargo(self):
        pass

    def _install_pip(self):
        pass

    def _install_conan(self):
        pass

    def _load_manifest(self):
        manifest = json.load( Path('./manifest.json').as_posix() )
        self.name = manifest['name']
        try:
            self.build_dependency = manifest['build']['dependency']
        except:
            self.build_dependency = None
        try:
            self.runtime_dependency = manifest['runtime']['dependency']
        except:
            self.runtime_dependency = None
        try:
            self.build_script = manifest['build']['script']
        except:
            self.build_script = None
        #
        self.output = manifest['output']
        pass

    def build(self, logger=None):
        try:
            self._load_manifest()
            _title = '[build] %s'
        except Exception as e:
            raise Exception(e)
        pass

    def install(self, logger=None):
        pass

    def test(self, logger=None):
        pass

    pass

def display_logo():
    with TypeWriter() as tw:
        tw.write(['Simple', ' Build', ' System'], 500, 'yellow', 'on_blue', True)
        tw.write( list(' for VDM Capability Library'), color='cyan' )
    pass

def validate_work_dirs(work_dirs):
    examiner = lambda _path: _path.is_dir() and (_path/'manifest.json').exists()
    if type(work_dirs) is not list:
        work_dirs = list( filter(examiner, Path('./').glob('*')) )
    else:
        work_dirs = list( filter(examiner, work_dirs) )
    return work_dirs

def apply(executor, work_dirs):
    for _dir in work_dirs:
        with halo.Halo('Simple Build System') as logger:
            with WorkSpace(_dir):
                try:
                    executor(logger)
                except Exception as e:
                    logger.fail(test=str(e))
                else:
                    logger.succeed()
        pass
    pass

def execute(sbs:SimpleBuildSystem, command:str, args):
    assert( isinstance(sbs, SimpleBuildSystem) )
    work_dirs = getattr(args, 'names', None)
    work_dirs = validate_work_dirs(work_dirs)

    if len(work_dirs)==0:
        return
    if not args.no_logo:
        display_logo()
    
    if command=='install':
        apply(sbs.install, work_dirs)
    elif command=='test':
        apply(sbs.test, work_dirs)
    else: #build
        apply(sbs.build, work_dirs)
    pass

def init_subparsers(subparsers):
    p_build = subparsers.add_parser('build')
    p_build.add_argument('names', metavar='name', nargs='*')
    #
    p_install = subparsers.add_parser('install')
    p_install.add_argument('names', metavar='name', nargs='*')
    #
    p_test = subparsers.add_parser('test')
    p_test.add_argument('names', metavar='name', nargs='*')
    pass

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(
            description='Simple Build System for VDM Capability Library.')
        parser.add_argument('--no-logo', action='store_true', default=False)
        subparsers = parser.add_subparsers(dest='command')
        init_subparsers(subparsers)
        #
        args = parser.parse_args()
        sbs = SimpleBuildSystem()
        execute(sbs, args.command, args)
    except Exception as e:
        raise e if DBG else ''
    finally:
        '' if DBG else exit()
    pass
