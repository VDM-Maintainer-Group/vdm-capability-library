#!/usr/bin/env python3
import configparser
import json
import os
from pathlib import Path
import subprocess as sp

import argparse
from pyvdm.interface.wrapper import jsonify

ROOT_FOLDER = os.getenv('VDM_CAPABILITY_INSTALL_DIRECTORY', Path('~/.vdm/capability').expanduser().as_posix() )
CONNECTOR_FOLDER = 'connector' if Path('connector').exists() else 'browser-bridge-connector'
EXTENSION_FOLDER = 'extension/packages' if Path('extension').exists() else 'browser-bridge-extensions'

CRX_ID = 'phmlhncfebmikfmkfombdjnkjmkpdjdl'
XPI_ID = 'browser-bridge@vdm-compatible.org'

SUPPORT = {
    ## chromium-based
    'google-chrome': {
        'id': CRX_ID,
        'type': 'chromium',
        'manifest':  '/etc/opt/chrome/native-messaging-hosts',
        'extension': '/opt/google/chrome/extensions'
    },
    'microsoft-edge': {
        'id': CRX_ID,
        'type': 'chromium',
        'manifest':  '/etc/opt/edge/native-messaging-hosts',
        'extension': '/usr/share/microsoft-edge/extensions'
    },
    'org.deepin.browser.desktop': {
        'id': CRX_ID,
        'type': 'chromium',
        'manifest':  '/etc/browser/native-messaging-hosts',
        'extension': '/usr/share/browser/extensions'
    },
    ## firefox
    'firefox-esr': {
        'id': XPI_ID,
        'type': 'firefox',
        'manifest':  '/usr/lib/mozilla/native-messaging-hosts',
        'extension': '/usr/lib/mozilla/extensions'
    }
}

MANIFEST = {
    'chromium': {
        'name': 'org.vdm.browser_bridge',
        'description': 'Native Messaging host configuration for VDM',
        'path': None,
        'type': 'stdio',
        'allowed_origins': [f'chrome-extension://{CRX_ID}/']
    },
    'firefox': {
        'name': 'org.vdm.browser_bridge',
        'path': None,
        'description': 'Native Messaging host configuration for VDM',
        'type': 'stdio',
        'allowed_extensions': [f'{XPI_ID}']
    }
}

def __version():
    if Path('manifest.json').exists():
        with open('manifest.json') as fp:
            return json.load(fp)['version']
    elif ( Path(ROOT_FOLDER)/'browser-bridge' ).exists():
        config = configparser.ConfigParser()
        config.read( Path(ROOT_FOLDER)/'browser-bridge'/'.conf' )
        return config['version']
    else:
        return '0.0.0'

CHROMIUM_EXTENSION = {
    'external_crx': f'{ROOT_FOLDER}/browser-bridge-extensions/chrome.crx',
    'version': __version()
}

class PrivilegeRunner():
    def __init__(self):
        self.commands = list()
        pass

    def add(self, *command):
        self.commands.extend(command)
        pass

    def run(self):
        command = json.dumps( ';'.join(self.commands) )
        command = f'pkexec sh -c {command}'
        sp.run(command, capture_output=True, check=True, shell=True)
        self.commands = list()
        pass

    pass

def __check(browser_name):
    _config = SUPPORT[browser_name]
    supported = True

    ## check connector
    connector_file = f'/opt/browser-bridge/connector_{browser_name}.py'
    supported &= Path(connector_file).exists()

    ## check connector manifest
    manifest_file = Path(_config['manifest'])/'org.vdm.browser_bridge.json'
    supported &= Path(manifest_file).exists()

    ## check extension
    extension_file = Path(_config['extension']) / (_config['id'] + '.json')
    supported &= Path(extension_file).exists()

    return supported

def __install(browser_name, sudo=None, lazy=False):
    _config = SUPPORT[browser_name]
    sudo = sudo if sudo else PrivilegeRunner()

    ## install global resources
    if not Path('/opt/browser-bridge/connector.py').exists():
        sudo.add(
            'mkdir -p /opt/browser-bridge',
            f'cp -f {CONNECTOR_FOLDER}/connector.py /opt/browser-bridge')

    ## install connector
    connector_file = f'connector_{browser_name}.py'
    sudo.add(
        f'ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/{connector_file}',
        f'mkdir -p {_config["manifest"]}')
    
    ## install connector manifest
    manifest = MANIFEST[ _config['type'] ]
    manifest['path'] = f'/opt/browser-bridge/{connector_file}'
    manifest = json.dumps(manifest)
    manifest_file = Path(_config['manifest'])/'org.vdm.browser_bridge.json'
    sudo.add(f'echo {manifest} > {manifest_file}')

    ## install extension
    sudo.add( f'mkdir -p {_config["extension"]}' )
    if _config['type']=='chromium':
        extension_file = Path(_config['extension']) / (_config['id'] + '.json')
        content = json.dumps(CHROMIUM_EXTENSION)
        sudo.add(f'echo {content} > {extension_file}')
    
    return sudo if lazy else sudo.run()

def __uninstall(browser_name, sudo=None, lazy=False):
    _config = SUPPORT[browser_name]
    sudo = sudo if sudo else PrivilegeRunner()

    ## uninstall connector and manifest
    connector_file = f'connector_{browser_name}.py'
    manifest_file = Path(_config['manifest'])/'org.vdm.browser_bridge.json'
    sudo.add(
        f'rm -f /opt/browser-bridge/{connector_file}',
        f'rm -f {manifest_file}')

    ## uninstall extension
    if _config['type']=='chromium':
        extension_file = Path(_config['extension']) / (_config['id'] + '.json')
        sudo.add(f'rm -f {extension_file}')

    return sudo if lazy else sudo.run()

@jsonify
def status(browsers:list):
    if browsers==['*'] or len(browsers)==0:
        browsers = SUPPORT
    status = [ __check(x) for x in browsers ]
    if True in status:
        return ''
    else:
        raise Exception('Not installed.')
    pass

@jsonify
def enable(browsers:list):
    if browsers==['*']:
        browsers = SUPPORT
    ##
    sudo = PrivilegeRunner()
    for x in browsers:
        sudo = __install(x, sudo, lazy=True)
    sudo.run()
    return ''

@jsonify
def disable(browsers:list):
    if browsers==['*']:
        browsers = SUPPORT
    ##
    sudo = PrivilegeRunner()
    for x in browsers:
        sudo = __uninstall(x, sudo, lazy=True)
    sudo.run()
    return ''

def main():
    parser = argparse.ArgumentParser(
        description='Browser-Bridge Capability Manager.')
    parser.add_argument('--work-dir', default=Path.cwd())
    subparsers = parser.add_subparsers(dest='command')
    p_status = subparsers.add_parser('status')
    p_status.add_argument('browsers',  nargs='*')
    p_enable = subparsers.add_parser('enable')
    p_enable.add_argument('browsers',  nargs='+')
    p_disable = subparsers.add_parser('disable')
    p_disable.add_argument('browsers', nargs='+')
    ##
    args = parser.parse_args()
    ##
    import json
    command_fn = {
        'status':status, 'enable':enable, 'disable':disable
    }.get(args.command, lambda _:'null')
    browsers  = args.browsers if 'browsers' in args else None
    arguments = json.dumps({ 'browsers':browsers })
    res = json.loads( command_fn(arguments) )
    print(res)
    pass

if __name__=='__main__':
    try:
        main()
    except Exception as e:
        raise e
    finally:
        pass
