#!/usr/bin/env python3
import os, sys, time, shutil, argparse, subprocess as sp
from pathlib import Path
import halo, termcolor, yaml
import json

DBG = 1
OUTPUT_DIRECTORY  = os.getenv('VDM_CAPABILITY_OUTPUT_DIRECTORY', './output')
INSTALL_DIRECTORY = os.getenv('VDM_CAPABILITY_INSTALL_DIRECTORY', '~/.vdm/capability')
POSIX = lambda x: x.as_posix()

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

    def __install_cargo(self, logger=None):
        pass

    def __install_pip(self, logger=None):
        pass

    def __install_conan(self, logger=None):
        pass

    def _check_dependency(self, dep_map:dict, logger=None):
        for cmd,args in dep_map.items():
            if cmd=='cargo':
                self.__install_cargo(logger)
                for arg in args:
                    logger.text = self._title%'cargo install %s'%arg
                    sp.check_call(['bash', '-c', 'cargo install "%s"'%arg],
                                    stdout=sp.PIPE, stderr=sp.PIPE)
                    # logger.succeed()
            elif cmd=='pip':
                self.__install_pip(logger)
                for arg in args:
                    logger.text = self._title%'pip3 install %s'%arg
                    sp.check_call(['bash', '-c', 'pip3 install "%s"'%arg],
                                    stdout=sp.PIPE, stderr=sp.PIPE)
                    # logger.succeed()
            elif cmd=='conan':
                self.__install_conan(logger)
                raise Exception('Conan is not supported now')
        pass

    def _copy_files(self, src_dir:Path, dst_dir:Path, logger=None):
        for src_file,dst_file in self.output:
            _dst_path = dst_dir/(dst_file if dst_file else src_file)
            _dst_path.parent.mkdir(parents=True, exist_ok=True)
            src_path = src_dir / src_file
            dst_path = _dst_path if dst_file else _dst_path.parent
            shutil.copy( POSIX(src_path.resolve()), POSIX(dst_path.resolve()) )
        pass

    def _exec_build(self, logger=None):
        for cmd in self.build_script:
            logger.text = self._title%'Building: %s'%cmd
            sp.check_call(['bash', '-c', cmd], stdout=sp.PIPE, stderr=sp.PIPE)
            pass
        pass

    def _write_config_file(self, manifest):
        _output = [ x[1] if x[1] else x[0] for x in self.output ]
        #
        cfg = {
            'entry':Path(_output[0]).name, 'files': _output,
            'runtime': manifest['runtime'],
            'metadata': {
                'name':manifest['name'], 'class':manifest['type'], 'version':manifest['version'],
                'func': {}
            }
        }
        #
        for name,meta in manifest['metadata'].items():
            cfg['metadata']['func'].update({
                name : { 'restype': meta['restype'], 'args': meta['args'] }
            })
        #
        _cfg_path = self.output_dir/self.name; _cfg_path.mkdir(parents=True, exist_ok=True)
        with open(_cfg_path/'.conf', 'w') as cfg_file:
            yaml.dump(cfg, cfg_file)
        pass

    def load_manifest(self):
        with open(Path('./manifest.json')) as fd:
            manifest = json.load( fd )
        try:
            self.name = manifest['name']
            self.output = manifest['build']['output']
        except Exception as e:
            raise Exception('%s section missing in maifest file.'%e)
        #
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
        _output = [x.split('@') for x in self.output]
        _output = [(x[0],None) if len(x)==1 else (x[0],x[1]) for x in _output]
        self.output = _output
        return manifest

    def build(self, logger=None):
        self._title = '[build] %s'
        try:
            self.load_manifest()
            self._title = '[%s] %s'%(self.name, '%s')
            #
            logger.text = self._title%'Check build dependency ...'
            self._check_dependency(self.build_dependency, logger)
            #
            logger.text = self._title%'Building ...'
            self._exec_build(logger)
            #
            logger.text = self._title%'Release output files ...'
            self._copy_files(Path('.'), self.output_dir)
            #
            logger.text = self._title%'build pass.'
        except Exception as e:
            msg = self._title%'build failed. ' + str(e)
            raise Exception(msg)
        pass

    def install(self, logger=None):
        self._title = '[install] %s'
        try:
            manifest = self.load_manifest()
            self._title = '[%s] %s'%(self.name, '%s')
            #
            logger.text = self._title%'Check runtime dependency ...'
            self._check_dependency(self.runtime_dependency, logger)
            #
            logger.text = self._title%'Generate .conf file ...'
            self._write_config_file(manifest)
            #
            logger.text = self._title%'Installing ...'
            _output = [x[1] if x[1] else x[0] for x in self.output]
            _output.append( POSIX(Path(self.name)/'.conf') )
            _output = [(x,None) for x in _output]
            self.output = _output
            self._copy_files(self.output_dir, self.install_dir)
            #
            logger.text = self._title%'Installed.'
        except Exception as e:
            msg = self._title%'install failed. ' + str(e)
            raise Exception(msg)
        pass

    def test(self, logger=None):
        self._title = '[test] %s'
        try:
            self.load_manifest()
            self._title = '[%s] %s'%(self.name, '%s')
            #
            logger.text = self._title%'test pass.'
        except Exception as e:
            msg = self._title%'test failed. ' + str(e)
            raise Exception(msg)
        pass

    pass

def display_logo():
    with TypeWriter() as tw:
        tw.write(['Simple', ' Build', ' System'], 500, 'yellow', 'on_blue', True)
        tw.write( list(' for VDM Capability Library'), color='cyan' )
        tw.write([''], duration=100)
    pass

def validate_work_dirs(work_dirs:list):
    examiner = lambda _path: _path.is_dir() and (_path/'manifest.json').exists()
    if len(work_dirs)==0:
        work_dirs = list( filter(examiner, Path('./').glob('*')) )
    else:
        work_dirs = [Path(_dir) for _dir in work_dirs]
        work_dirs = list( filter(examiner, work_dirs) )
    return work_dirs

def apply(executor, work_dirs):
    for _dir in work_dirs:
        with halo.Halo('Simple Build System') as logger:
            with WorkSpace(_dir):
                try:
                    executor(logger)
                except Exception as e:
                    logger.fail(text=str(e))
                else:
                    logger.succeed()
        pass
    pass

def execute(sbs:SimpleBuildSystem, command:str, args):
    assert( isinstance(sbs, SimpleBuildSystem) )
    work_dirs = getattr(args, 'names', [])
    work_dirs = validate_work_dirs(work_dirs)

    if len(work_dirs)==0:
        return
    
    if command=='install':
        apply(sbs.install, work_dirs)
    elif command=='test':
        apply(sbs.test, work_dirs)
    else: #build
        if not args.no_logo_show:
            display_logo()
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
        parser.add_argument('--no-logo-show', action='store_true', default=False)
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
