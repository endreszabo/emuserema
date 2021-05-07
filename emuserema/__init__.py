#!/usr/bin/env python3

from os.path import expanduser
from sys import exit, argv
from emuserema.plugin_manager import PluginManager
from emuserema.services import AbstractService
from emuserema.world import World
from emuserema.yamlloader import EmuseremaYamlLoader
from ruamel.yaml import dump
from emuserema.utils import traverse, get_default_directory
from emuserema.services import *
from emuserema.redirects import RedirectFactory
# if yaml dumping is to be enabled:
from sys import stdout


class Emuserema(object):
    def __init__(self, definitions_directory=None):
        self._definitions_directory = get_default_directory(definitions_directory)

        self.yamlloader = EmuseremaYamlLoader(self._definitions_directory)
        self.redirect_factory = RedirectFactory(definitions_directory=self._definitions_directory,
                yamlloader=self.yamlloader)
        self.service_factory = ServiceFactory()

        self.services = {}
        self.worlds = {}

        self.load()
        self.process()


    def __del__(self):
        """Commit changes. For example new redirects to .redirects.yaml"""
        self.commit()

    def service_builder(self, path, obj):
        """Iterate over YAML entries replacing them with objects based on those definitions."""
        if path and path[0] == 'defaults':
            return obj
        if isinstance(obj, dict):
            if '_type' in obj:
                if self.service_factory.supported(obj):
                    service = self.service_factory.create(path, **obj)
                    self.services[service.tag] = service
                    return service
                else:
                    raise NotImplementedError("Object type of '%s' is not supported" % obj['_type'])
        return obj

    def via_resolver(self, path, service):
        """Resolve cross references between objects."""
        if path and path[0] == 'defaults':
            return service
        if isinstance(service, AbstractService):
            if service.via is None:
                return service
            service.via = self.services[service.via]
        return service

    def create_worlds(self, path, service):
        """Organize service object into their respective worlds."""
        if path and path[0] == 'defaults':
            return service
        if isinstance(service, AbstractService):
            if service.world not in self.worlds:
                self.worlds[service.world] = World(service.world)
            #service.world=worlds[service.world]
            self.worlds[service.world].append(service)

        return service

    def redirector(self, path, service):
        """Process redirect dependencies"""
        if path and path[0] == 'defaults':
            return service
        if isinstance(service, AbstractService):
            if service.via is None:
                return service
            service.process_proxy(service.via, self.redirect_factory)

        return service

    def load(self):
        self.data = self.yamlloader.loadyaml('emuserema.yaml')

    def process(self):
        """Iterate over definitions tree a numerous times"""
        self.data = traverse(self.data, callback=self.service_builder)
        self.data = traverse(self.data, callback=self.via_resolver)
        self.data = traverse(self.data, callback=self.redirector)
        self.data = traverse(self.data, callback=self.create_worlds)

    def dump(self):
        dump(self.data, stdout, default_flow_style=False)

    def render(self):
        config = self.yamlloader.loadyaml('config.yaml')

        renderer_plugins = PluginManager('emuserema.plugins.renderers', config=config['plugins']['renderers'])

        renderer_plugins.run_selected(filter(lambda name: config['plugins']['renderers'][name]['enabled'] is True,
            config['plugins']['renderers']), worlds=self.worlds, services=self.services)


    def populate_ansible_inventory(self, inventory=None, world='default'):
        """function to populate Ansible inventory on the spot"""

        def get_ansible_treevars(data, data_path):
            """Acquires the _ansible_treevars items from the main data dict"""
            if len(data_path) > 1:
                yield from get_ansible_treevars(data[data_path[0]], data_path[1:])
            #elif isinstance(data.get(data_path[0]), dict):
            yield data.get(data_path[0]).get('_ansible_treevars')

        def inherit(ansible_treevars_items):
            """Renders the actual inheritance that it gets back from get_ansible_treevars()"""
            retval_dict = dict()
            for ansible_treevars_item in ansible_treevars_items:
                #a leaf with a value
                if ansible_treevars_item:
                    print('item', ansible_treevars_item)
                    for ansible_treevars_dict in ansible_treevars_item:
                        for key, value in ansible_treevars_dict.items():
                            if isinstance(value, str):
                                if key not in retval_dict:
                                    retval_dict[key] = [value]
                                else:
                                    retval_dict[key].append(value)
                                    #retval_dict[key].insert(0, value)
                            elif isinstance(value, int):
                                if key not in retval_dict:
                                    retval_dict[key] = [str(value)]
                                else:
                                    retval_dict[key].append(str(value))
                                    #retval_dict[key].insert(0, value)
                            else:
                                raise NotImplementedError(
                                    '_ansible_treevars item with a type of %s is unsupported.' % type(value))
            print('treevars items:', retval_dict)
            for key, value in retval_dict.items():
                yield [key, value]

        world = self.worlds[world]
        for service in self.services:
            service = self.services[service]
            if self.worlds[service.world] == world:
                if isinstance(service, (SSHservice, DummyService)) or '_ansible_hostvars' in service.kwargs:
                    inventory.add_host(service.tag)
                    inventory.set_variable(service.tag, 'ansible_ssh_common_args',
                        '-F ~/.ssh/configs/%s' % service.world)
                    #we must fix this somehow
                    #inventory.set_variable(service.tag, 'ansible_ssh_executable',
                    #    'SSH_AUTH_SOCK=/home/e/.ssh/agents/%s /usr/bin/ssh' % service.world)
                    # iterate over the data tree to get _ansible_treevars items
                    for key, value in inherit(get_ansible_treevars(self.data, service.path)):
                        print("setting treevars variable", key, value)
                        inventory.set_variable(service.tag, key, value)
                    if '_ansible_hostvars' in service.kwargs:
                        for key, value in service.kwargs['_ansible_hostvars'].items():
                            inventory.set_variable(service.tag, key, value)
                    if '_ansible_groups' in service.kwargs:
                        for group in service.kwargs['_ansible_groups']:
                            group = group.lower().replace(' ', '_')
                            group = inventory.add_group(group)
                            inventory.add_child(group, service.tag)
                    group = inventory.add_group('class_%s' % service.__class__.__name__)
                    inventory.add_child(group, service.tag)
                    for group in service.path[1:-1] + ['emuserema_' + '__'.join(service.path[1:-1])]:
                        group = group.lower().replace(' ', '_')
                        group = inventory.add_group(group)
                        inventory.add_child(group, service.tag)
#        embed()
        pass

    def commit(self):
        self.redirect_factory.commit()


def main():
    emuserema = Emuserema()
    if len(argv) > 1:
        if argv[1] == '-t':
            print("Configuration parsing was successful.")
            exit(0)
    emuserema.render()


if __name__ == '__main__':
    main()
