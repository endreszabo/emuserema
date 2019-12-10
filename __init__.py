#!/usr/bin/env python3

from os.path import expanduser
from sys import exit, argv
from plugin_manager import PluginManager
from services import AbstractService
from world import World
from yamlloader import loadyaml
from utils import traverse
from services import *
from redirects import RedirectFactory
# if yaml dumping is to be enabled:
#from yamlloader import dump
#from sys import stdout

PREFIX = expanduser("~")
CFGDIR = PREFIX + '/etc'
LIBDIR = PREFIX + '/local/lib/emuserema'
DESTINATION_HOSTS_FILE = PREFIX + '/etc/emuserema/per-destination-commands'


service_factory = ServiceFactory()
services = {}

redirect_factory = RedirectFactory()

worlds = {}


def service_builder(path, obj):
    if path and path[0] == 'defaults':
        return obj
    if isinstance(obj, dict):
        if '_type' in obj:
            if service_factory.supported(obj):
                service = service_factory.create(path, **obj)
                services[service.tag] = service
                return service
            else:
                raise NotImplementedError("Object type of '%s' is not supported" % obj['_type'])
    return obj


def via_resolver(path, service):
    if path and path[0] == 'defaults':
        return service
    if isinstance(service, AbstractService):
        if service.via is None:
            return service
        service.via = services[service.via]
    return service


def redirector(path, service):
    if path and path[0] == 'defaults':
        return service
    if isinstance(service, AbstractService):
        if service.via is None:
            return service
        service.process_proxy(service.via, redirect_factory)

    return service


def create_worlds(path, service):
    if path and path[0] == 'defaults':
        return service
    if isinstance(service, AbstractService):
        if service.world not in worlds:
            worlds[service.world] = World(service.world)
        #service.world=worlds[service.world]
        worlds[service.world].append(service)

    return service


class Emuserema(object):
    def __init__(self, definitions='emuserema.yaml', config='config.yaml'):
        self._definitions = definitions
        self._config = config
        self.load()

    def __del__(self):
        self.commit()

    def load(self):
        self.data = loadyaml(self._definitions)

        self.data = traverse(self.data, callback=service_builder)
        self.data = traverse(self.data, callback=via_resolver)
        self.data = traverse(self.data, callback=redirector)
        self.data = traverse(self.data, callback=create_worlds)
        #dump(self.data, stdout, default_flow_style=False)

    def render(self):
        config = loadyaml('config.yaml')

        renderer_plugins = PluginManager('plugins.renderers')

        renderer_plugins.run_selected(filter(lambda enabled: config['plugins_enabled']['renderers'][enabled] == True, config['plugins_enabled']['renderers']), worlds=worlds, services=services)

    def populate_ansible_inventory(self, inventory=None, world='default'):
        pass

    def commit(self):
        redirect_factory.commit()


def main():
    emuserema = Emuserema()
    if len(argv) > 1:
        if argv[1] == '-t':
            print("Configuration parsing was successful.")
            exit(0)
    emuserema.render()


if __name__ == '__main__':
    main()
