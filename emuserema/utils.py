from os import makedirs
from os.path import expanduser, dirname, abspath, join as pathjoin, isfile
from os import walk, path
from shutil import rmtree
from os import listdir, unlink

#from __future__ import print_function


def cleanup_dir(target):
    for root, dirs, files in walk(target, topdown=False):
        for name in dirs:
            try:
                pass
                rmtree(path.join(root, name))
            except OSError as e:
                print("Ran into an exception during removal of %s: '%s'" % (path.join(root, name), e))


def cleanup_files(folder):
    for the_file in listdir(folder):
        file_path = path.join(folder, the_file)
        if not path.islink(file_path) and path.isfile(file_path):
            pass
            unlink(file_path)


def makedir_getfd(target):
    target = expanduser(target)
    makedirs(target[:target.rindex('/')], exist_ok=True)
    return open(target, 'w')


def service_paths_to_tree(services):
    #A simple recursion will do -- they said
    #https://codegolf.stackexchange.com/a/4485
    def build_nested_helper(path, service, container):
        segs = path
        head = segs[0]
        tail = segs[1:]
        if not tail:
            container.append({
                "text": "%s [%s]%s" % (service.tag, service.original_url,
                    service.via and " (via %s)" % service.via.tag or ''),
                "type": "website",
                "a_attr": {
                    "href": service.url
                }
            })
        else:
            #folder = {'service':head,'children': []}
            for item in container:
                if item['text'] == head:
                    build_nested_helper(tail, service, item['children'])
                    break
            else:
                folder = {
                    "type": "leaf",
                    "text": head,
                    "children": []
                }
                container.append(folder)
                build_nested_helper(tail, service, folder['children'])

    def build_nested(paths):
        container = []
        for item in paths:
            build_nested_helper(item[0], item[1], container)
        return container
    return build_nested(services)


def traverse(obj, item=None, callback=None):
    if item is None:
        item = []

    if isinstance(obj, dict):
        #if '_type' in obj:
        #    return obj['_type']
        value = {k: traverse(v, item + [k], callback)
                 for k, v in obj.items()}
    elif isinstance(obj, list):
        value = [traverse(elem, item + [[]], callback)
                 for elem in obj]
    else:
        value = obj

    if callback is None:
        return value
    else:
        return callback(item, value)


def get_default_directory(directory=None):
    from os import environ, getuid
    if 'VIRTUAL_ENV' in environ:
        return environ['VIRTUAL_ENV']+'/etc/emuserema'
    if getuid() == 0:
        return '/etc/emuserema'
    if directory is None:
        directory = '~/.config/emuserema'
    return expanduser(directory)


def generate_initial_config(target):
    target = get_default_directory(target)
    makedirs(target, exist_ok=True)
    with open(target+'/config.yaml', 'w') as config:
        print("""
plugins:
  renderers:
    openssh:
      enabled: True
      output_dir: ~/.ssh/configs
    putty:
      enabled: False
      output_dir: ~/Documents/SSH
      one_registry_file_per_world: True
    wssh_commands:
      enabled: False
      output_file: ~/.config/emuserema/.wssh_commands
    realvnc:
      enabled: False
      output_dir: ~/.vnc/VNCAddressBook
      clear_dir: True
    jstree:
      enabled: False
      output_dir: ~/htdocs
    mstsc:
      enabled: False
      output_dir: ~/Documents/RDP
""", file = config)

    with open(target+'/emuserema.yaml', 'w') as default_emuserema:
        print("""
---
defaults:
  all: &defaults
    ControlMaster: auto
    ControlPersist: 0
    ControlPath: ~/.ssh/masters/%r@%n:%p.global
    UserKnownHostsFile: ~/.ssh/hosts/global
    Protocol: 2
    ServerAliveInterval: 15
    ServerAliveCountMax: 3
    TCPKeepAlive: yes
    User: root
    HashKnownHosts: no
    VisualHostKey: no
    ForwardAgent: yes
    _hostkeyalias: True
    _type: ssh
    Port: 22
  defaults-myuser: &defaults-myuser
    <<: *defaults
    User: myuser
  oldgear: &oldgear
    KexAlgorithms: diffie-hellman-group1-sha1
    Ciphers: aes256-cbc
  reallyoldgear: &reallyoldgear
    <<: *oldgear
    HostKeyAlgorithms: ssh-dss
""", file = default_emuserema)

    with open(target+'/.redirects.yaml', 'w') as redirects:
        print("""
bindip: 127.0.0.1
counter: 38000
""", file = redirects)

def get_template(module, name):
    if isfile(pathjoin(get_default_directory(), 'templates', module, name)):
        return pathjoin(get_default_directory(), 'templates', module, name)
    return pathjoin(dirname(abspath(__file__)), 'templates', module, name)
 
