#!/usr/bin/env python3

from os.path import expanduser
from sys import exit
from plugin_manager import PluginManager

PREFIX=expanduser("~")
CFGDIR=PREFIX+'/etc'
LIBDIR=PREFIX+'/local/lib/emuserema'
DESTINATION_HOSTS_FILE=PREFIX+'/etc/emuserema/per-destination-commands'

from yamlloader import loadyaml, dump
from utils import traverse

from sys import exit, stdout

from services import *
service_factory = ServiceFactory()
services={}

from redirects import RedirectFactory
redirect_factory=RedirectFactory()

from world import World
worlds={}


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


def main():
    data=loadyaml('emuserema.yaml')

    config=loadyaml('config.yaml')

    data=traverse(data, callback=service_builder)

    data=traverse(data, callback=via_resolver)

    data=traverse(data, callback=redirector)

    data=traverse(data, callback=create_worlds)

    renderer_plugins = PluginManager('plugins.renderers')

    renderer_plugins.run_selected(filter(lambda enabled: config['plugins_enabled']['renderers'][enabled] == True, config['plugins_enabled']['renderers']), worlds=worlds, services=services)

    redirect_factory.commit()

    #dump(data, stdout, default_flow_style=False)

if __name__ == '__main__':
    main()
