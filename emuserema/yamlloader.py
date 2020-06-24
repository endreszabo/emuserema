#import ruamel.yaml

#from ruamel.std.pathlib import Path
#from ruamel.yaml import YAML, version_info, dump, YAMLError, SafeLoader, RoundTripLoader
#from ruamel.yaml import YAML, YAMLError, dump, SafeLoader
import ruamel.yaml
from os.path import isfile
from jinja2 import Template, ChoiceLoader, PackageLoader, FileSystemLoader, Environment
from os import environ, uname


class EmuseremaRelativeSafeLoader(ruamel.yaml.SafeLoader):
    def __init__(self, definitions_directory=None):
        self._definitions_directory = definitions_directory

        if ruamel.yaml.version_info < (0, 15):
            self.yaml = ruamel.yaml
        else:
            self.yaml = ruamel.yaml.YAML(typ='safe', pure=True)
            self.yaml.default_flow_style = False
        self.jinja_env = Environment(loader=ChoiceLoader([
            PackageLoader('emuserema'),
            FileSystemLoader(searchpath=self._definitions_directory, followlinks=True)
        ]))

    def construct_python_tuple(self, cons, node):
        return tuple(cons.construct_sequence(node))

    # adapted from http://code.activestate.com/recipes/577613-yaml-include-support/
    def yaml_include(self, cons, node):
        path =  node.value
        if isfile(self._definitions_directory + '/' +path + '.j2'):
            templatedata = self.loadyaml(path + '.j2.yaml')
            if not templatedata:
                templatedata = {}
            templatedata['_environ'] = dict(environ)
            if 'HOSTNAME' not in templatedata['_environ']:
                uname_result = uname()
                templatedata['_environ']['HOSTNAME'] = uname_result.nodename
            template = self.jinja_env.get_template(path + '.j2')
            y = cons.loader
            yaml = ruamel.yaml.YAML(typ=y.typ, pure=y.pure)
            yaml.composer.anchors = cons.composer.anchors
            return yaml.load(template.render(templatedata))
        with open(self._definitions_directory + '/' +path, 'r') as infile:
            if ruamel.yaml.version_info < (0, 15):
                #yaml.composer.anchors = cons.composer.anchors
                return ruamel.yaml.safe_load(infile)
            else:
                y = cons.loader
                yaml = ruamel.yaml.YAML(typ=y.typ, pure=y.pure)
                yaml.composer.anchors = cons.composer.anchors
                return yaml.load(infile)

    def loadyaml(self, filename):
        yamldata = None
        path = self._definitions_directory + '/' + filename
        if isfile(path + '.j2'):
            templatedata = self.loadyaml(filename + '.j2.yaml')
            templatedata['_environ'] = dict(environ)
            if 'HOSTNAME' not in templatedata['_environ']:
                uname_result = uname()
                templatedata['_environ']['HOSTNAME'] = uname_result.nodename
            template = self.jinja_env.get_template(self._definitions_directory + '/' + filename + '.j2')
            yamldata = self.yaml.load(template.render(templatedata))
        else:
            with open(path, 'r') as stream:
                try:
                    if ruamel.yaml.version_info < (0, 15):
                        yamldata = self.yaml.load(stream, Loader=ruamel.yaml.Loader)
                    else:
                        yamldata = self.yaml.load(stream)
            #        print(dump(t, default_flow_style=False))
            #        print type(t)
                except ruamel.yaml.YAMLError as exc:
                    print(exc)

        return yamldata

class EmuseremaYamlLoader(object):
    def __init__(self, definitions_directory=None):
        self._definitions_directory = definitions_directory

        if ruamel.yaml.version_info < (0, 15):
            self.yaml = ruamel.yaml
        else:
            self.yaml = ruamel.yaml.YAML(typ='safe', pure=True)
            self.yaml.default_flow_style = False

        self.jinja_env = Environment(loader=ChoiceLoader([
            PackageLoader('emuserema'),
            FileSystemLoader(searchpath=self._definitions_directory, followlinks=True)
        ]))

        def my_compose_document(self):
            if ruamel.yaml.version_info < (0, 15):
                self.get_event()
                node = self.compose_node(None, None)
                self.get_event()
            else:
                self.parser.get_event()
                node = self.compose_node(None, None)
                self.parser.get_event()
            # self.anchors = {}    # <<<< commented out
            return node

        if ruamel.yaml.version_info < (0, 15):
            pass
            self.yaml.composer.Composer.compose_document = my_compose_document
        else:
            self.yaml.Composer.compose_document = my_compose_document

        loader = EmuseremaRelativeSafeLoader(self._definitions_directory)

        if ruamel.yaml.version_info < (0, 15):
            self.yaml.add_constructor('!include', loader.yaml_include)
            self.yaml.add_constructor('tag:yaml.org,2002:python/tuple', loader.construct_python_tuple)
        else:
            self.yaml.Constructor.add_constructor('!include', loader.yaml_include)
            self.yaml.Constructor.add_constructor('tag:yaml.org,2002:python/tuple', loader.construct_python_tuple)

    def loadyaml(self, filename):
        yamldata = None
        path = self._definitions_directory + '/' + filename
        if isfile(path + '.j2'):
            templatedata = self.loadyaml(filename + '.j2.yaml')
            templatedata['_environ'] = dict(environ)
            if 'HOSTNAME' not in templatedata['_environ']:
                uname_result = uname()
                templatedata['_environ']['HOSTNAME'] = uname_result.nodename
            template = self.jinja_env.get_template(filename + '.j2')
            yamldata = self.yaml.load(template.render(templatedata))
        else:
            with open(path, 'r') as stream:
                try:
                    if ruamel.yaml.version_info < (0, 15):
                        yamldata = self.yaml.load(stream, Loader=ruamel.yaml.Loader)
                    else:
                        yamldata = self.yaml.load(stream)
            #        print(dump(t, default_flow_style=False))
            #        print type(t)
                except ruamel.yaml.YAMLError as exc:
                    print(exc)

        if not yamldata:
            print(yamldata)
            raise ValueError("Failed to parse YAML Data")
        return yamldata

    def dumpyaml(self, data, filename):

        with open(self._definitions_directory + '/' + filename, 'w') as stream:
            ruamel.yaml.dump(data, stream, default_flow_style=False)
