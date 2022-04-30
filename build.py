#!/usr/bin/env python3
import os, sys, time, argparse, subprocess as sp
from pathlib import Path
import json, yaml, tempfile
import halo, termcolor

DBG = 1
POSIX = lambda x: x.as_posix()
SHELL_RUN = lambda x: sp.run(x, capture_output=True, check=True, shell=True)

OUTPUT_DIRECTORY  = os.getenv('VDM_CAPABILITY_OUTPUT_DIRECTORY',
                        POSIX( Path('./output').resolve() ))
INSTALL_DIRECTORY = os.getenv('VDM_CAPABILITY_INSTALL_DIRECTORY',
                        POSIX( Path('~/.vdm/capability').expanduser() ))
if os.getenv('SBS_EXECUTABLE') is None:
    os.environ['SBS_EXECUTABLE'] = POSIX( Path(__file__).resolve() )

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

class NoneLogger:
    __slots__ = ['text', 'enabled']

class SimpleBuildSystem:
    def __init__(self):
        self.output_dir = Path(OUTPUT_DIRECTORY)
        self.install_dir = Path(INSTALL_DIRECTORY)

        os.environ['LD_LIBRARY_PATH'] = f"{os.getenv('LD_LIBRARY_PATH','')}:{self.install_dir}"
        os.environ['PYTHONPATH'] = f"{os.getenv('PYTHONPATH','')}:{self.install_dir}"
        os.environ['CPATH'] = f"{os.getenv('CPATH','')}:{self.install_dir}/include"
        os.environ['LIBRARY_PATH'] = f"{os.getenv('LIBRARY_PATH','')}:{self.install_dir}"
        pass

    def __install_cargo(self):
        try:
            SHELL_RUN('which rustup cargo')
        except:
            try:
                SHELL_RUN('curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y')
            except:
                raise Exception('Rustup installation failed.')
        pass

    def __install_pip(self):
        try:
            SHELL_RUN('which pip3')
        except:
            try:
                SHELL_RUN('python3 < <(curl -sSf https://bootstrap.pypa.io/get-pip.py)')
            except:
                raise Exception('pip3 installation failed.')
        pass

    def __install_conan(self):
        try:
            SHELL_RUN('which conan')
        except:
            try:
                SHELL_RUN('pip3 install conan')
            except:
                raise Exception('Conan installation failed.')
        pass

    def _check_dependency(self, dep_map:dict, logger=NoneLogger):
        for cmd,args in dep_map.items():
            if cmd=='cargo':
                self.__install_cargo()
                _command = 'cargo install "%s"'
            elif cmd=='pip':
                self.__install_pip()
                _command = 'pip3 install "%s"'
            elif cmd=='conan':
                self.__install_conan()
                raise Exception('Conan is not supported now.')
            elif cmd=='apt':
                _command = 'sudo apt install "%s"'
            elif cmd=='sbs':
                _command = '$SBS_EXECUTABLE install "%s"'
            else:
                return

            for arg in args:
                logger.text = self._title%_command%arg
                SHELL_RUN(_command%arg)
        pass

    def __output_files(self, cmd:str, src_dir:Path, dst_dir:Path, ignore:bool):
        for src_file,dst_file in self.output:
            try:
                _dst_path = dst_dir/(dst_file if dst_file else src_file)
                _dst_path.parent.mkdir(parents=True, exist_ok=True)
                src_path = src_dir / src_file
                dst_path = _dst_path if dst_file else _dst_path.parent
                SHELL_RUN( f'{cmd} {POSIX(src_path.resolve())} {POSIX(dst_path.resolve())}' )
            except Exception as e:
                if not ignore: raise e
        pass

    def _copy_files(self, src_dir:Path, dst_dir:Path, ignore=False):
        self.__output_files('cp -r', Path(src_dir), Path(dst_dir), ignore)
        pass

    def _remove_files(self, src_dir:Path, ignore=True):
        dst_dir = tempfile.TemporaryDirectory().name
        self.__output_files('rm -rf', Path(src_dir), Path(dst_dir), ignore)
        pass

    def _exec_build(self, logger=NoneLogger):
        for i, cmd in enumerate(self.build_script):
            logger.text = self._title%'Building: %s'%cmd
            try:
                SHELL_RUN(cmd)
            except Exception as e:
                if isinstance(e, sp.CalledProcessError):
                    msg = e.stderr.decode().lstrip('/bin/sh: 1: ').rstrip()
                    msg = f'\n[build.script] {i+1}: ' + msg 
                else:
                    msg = str(e)
                raise Exception(msg)
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

    def load_config_file(self):
        with open(Path('.conf')) as fd:
            config = yaml.load(fd, Loader=yaml.CLoader)
        self.name = Path('.').resolve().name
        self.entry = config['entry']
        self.output = [(_file,None) for _file in config['files']]
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
            self.build_dependency = dict()
        try:
            self.runtime_dependency = manifest['runtime']['dependency']
        except:
            self.runtime_dependency = dict()
        try:
            self.build_script = manifest['build']['script']
        except:
            self.build_script = list()
        #
        _output = [x.split('@') for x in self.output]
        _output = [(x[0],None) if len(x)==1 else (x[0],x[1]) for x in _output]
        self.output = _output
        return manifest


    def build(self, logger=NoneLogger):
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
            msg = self._title%'build failed. ' + termcolor.colored(str(e), 'red')
            raise Exception(msg)
        pass

    def clean(self, logger=NoneLogger):
        self._title = '[clean] %s'
        try:
            _manifest = self.load_manifest()
            self._title = '[%s] %s'%(self.name, '%s')
            #
            _output = [x[1] if x[1] else x[0] for x in self.output]
            _output.append( POSIX(Path(self.name)/'.conf') )
            _output = [(x,None) for x in _output]
            self.output = _output
            self._remove_files(self.output_dir)
            # cleanup empty folders
            SHELL_RUN(f'find {self.output_dir} -type d -empty -delete')
            #
            if 'clean' in _manifest:
                _path_root = POSIX( Path('.').resolve() )
                _path_filter = lambda x: os.path.commonprefix([x, _path_root]) == _path_root
                #
                path_temp = [ POSIX(Path(x).resolve()) for x in _manifest['clean'] ]
                path_temp = filter(_path_filter, path_temp)
                SHELL_RUN( 'rm -rf %s'%(' '.join(path_temp)) )
            #
            logger.text = self._title%'Cleanup.'
        except Exception as e:
            raise e
        pass

    def install(self, logger=NoneLogger):
        self._title = '[install] %s'
        try:
            manifest = self.load_manifest()
            self._title = '[%s] %s'%(self.name, '%s')
            # check build outputs
            logger.text = self._title%'Check building results ...'
            try:
                self._copy_files(Path('output'), self.output_dir)
            except:
                if logger.enabled:
                    self.build(logger)
                else:
                    logger.enabled = True; logger.start()
                    self.build(logger); logger.succeed()
                    logger.enabled = False
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
            msg = self._title%'install failed. ' + termcolor.colored(str(e), 'red')
            raise Exception(msg)
        pass

    def uninstall(self, logger=NoneLogger):
        self._title = '[uninstall] %s'
        try:
            _manifest = self.load_config_file()
            self._title = '[%s] %s'%(self.name, '%s')
            #
            logger.text = self._title%'Uninstalling ...'
            _output = [POSIX( Path('..', x[1] if x[1] else x[0]) ) for x in self.output]
            _output.append('.conf')
            _output = [(x,None) for x in _output]
            self.output = _output
            self._remove_files(Path('.'), ignore=True)
            # cleanup empty folders
            SHELL_RUN(f'find {self.install_dir} -type d -empty -delete')
            #
            logger.text = self._title%'Uninstalled.'
        except Exception as e:
            msg = self._title%'uninstall failed. ' + termcolor.colored(str(e), 'red')
            raise Exception(msg)
        pass

    def test(self, logger=NoneLogger):
        self._title = '[test] %s'
        try:
            self.load_manifest()
            self._title = '[%s] %s'%(self.name, '%s')
            # check build outputs
            logger.text = self._title%'Check building results ...'
            try:
                self._copy_files(Path('.'), self.output_dir)
            except:
                self.build(logger)
            #
            #TODO: no test procedure provided now
            #
            logger.text = self._title%'test pass.'
        except Exception as e:
            msg = self._title%'test failed. ' + termcolor.colored(str(e), 'red')
            raise Exception(msg)
        pass

    pass

def display_logo():
    with TypeWriter() as tw:
        tw.write(['Simple', ' Build', ' System'], 500, 'yellow', 'on_blue', True)
        tw.write( list(' for VDM Capability Library'), color='cyan' )
        tw.write([''], duration=100)
    pass

def validate_work_dirs(command:str, work_dirs:list):
    if command=='uninstall':
        examiner = lambda _path: _path.is_dir() and (_path/'.conf').exists()
        work_dirs = [Path(INSTALL_DIRECTORY)/Path(_dir) for _dir in work_dirs]
        work_dirs = list( filter(examiner, work_dirs) )
    else:
        examiner = lambda _path: _path.is_dir() and (_path/'manifest.json').exists()
        if len(work_dirs)==0:
            work_dirs = list( filter(examiner, Path('./').glob('*')) )
        else:
            work_dirs = [Path(_dir) for _dir in work_dirs]
            work_dirs = list( filter(examiner, work_dirs) )
    return work_dirs

def apply(executor, work_dirs, enable_halo=False):
    ret = list()

    for _dir in work_dirs:
        try:
            with halo.Halo('Simple Build System', enabled=enable_halo) as logger:
                with WorkSpace(_dir):
                    try:
                        executor(logger)
                    except Exception as e:
                        logger.fail(text=str(e))
                        ret.append( str(e) )
                    else:
                        logger.succeed()
                        ret.append( True )
        except:
            ret.append(False)
    
    return ret

def execute(sbs:SimpleBuildSystem, command:str, work_dirs, logo_show_flag, enable_halo):
    assert( isinstance(sbs, SimpleBuildSystem) )
    if len(work_dirs)==0:
        return None
    
    if command=='install':
        return apply(sbs.install, work_dirs, enable_halo)
    elif command=='uninstall':
        return apply(sbs.uninstall, work_dirs, enable_halo)
    elif command=='test':
        return apply(sbs.test, work_dirs, enable_halo)
    elif command=='clean':
        return apply(sbs.clean, work_dirs, enable_halo)
    elif command=='build' or command==None:
        if command==None and logo_show_flag:
            display_logo()
        return apply(sbs.build, work_dirs, enable_halo)
    else:
        return None
    pass

def sbs_entry(command, work_dirs, logo_show_flag=False, enable_halo=False):
    sbs = SimpleBuildSystem()
    work_dirs = validate_work_dirs(command, work_dirs)
    return execute(sbs, command, work_dirs, logo_show_flag, enable_halo)

def init_subparsers(subparsers):
    p_build = subparsers.add_parser('build')
    p_build.add_argument('names', metavar='name', nargs='*')
    #
    p_build = subparsers.add_parser('clean')
    p_build.add_argument('names', metavar='name', nargs='*')
    #
    p_install = subparsers.add_parser('install')
    p_install.add_argument('names', metavar='name', nargs='*')
    #
    p_uninstall = subparsers.add_parser('uninstall')
    p_uninstall.add_argument('names', metavar='name', nargs=1)
    #
    p_test = subparsers.add_parser('test')
    p_test.add_argument('names', metavar='name', nargs='*')
    pass

def main():
    parser = argparse.ArgumentParser(
        description='Simple Build System for VDM Capability Library.')
    parser.add_argument('--no-logo-show', action='store_true', default=False)
    subparsers = parser.add_subparsers(dest='command')
    init_subparsers(subparsers)
    #
    args = parser.parse_args()
    work_dirs = getattr(args, 'names', [])
    logo_show_flag = not args.no_logo_show
    sbs_entry(args.command, work_dirs, logo_show_flag, True)
    pass

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        raise e if DBG else ''
    finally:
        '' if DBG else exit()
    pass
