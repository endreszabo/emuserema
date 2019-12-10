#import ruamel.yaml

#from ruamel.std.pathlib import Path
#from ruamel.yaml import YAML, version_info, dump, YAMLError, SafeLoader, RoundTripLoader
from ruamel.yaml import YAML, YAMLError, dump, SafeLoader


class EmuseremaRelativeSafeLoader(SafeLoader):
    def __init__(self, definitions_directory=None):
        self._definitions_directory = definitions_directory

    def construct_python_tuple(self, cons, node):
        return tuple(cons.construct_sequence(node))

    # adapted from http://code.activestate.com/recipes/577613-yaml-include-support/
    def yaml_include(self, cons, node):
        y = cons.loader
        yaml = YAML(typ=y.typ, pure=y.pure)  # same values as including YAML
        yaml.composer.anchors = cons.composer.anchors
        with open(self._definitions_directory + '/' + node.value, 'r') as infile:
            return yaml.load(infile)


class EmuseremaYamlLoader(object):
    def __init__(self, definitions_directory=None):
        self._definitions_directory = definitions_directory

        self.yaml = YAML(typ='safe', pure=True)
        self.yaml.default_flow_style = False

        def my_compose_document(self):
            self.parser.get_event()
            node = self.compose_node(None, None)
            self.parser.get_event()
            # self.anchors = {}    # <<<< commented out
            return node

        self.yaml.Composer.compose_document = my_compose_document

        loader = EmuseremaRelativeSafeLoader(self._definitions_directory)

        self.yaml.Constructor.add_constructor('!include', loader.yaml_include)
        self.yaml.Constructor.add_constructor('tag:yaml.org,2002:python/tuple', loader.construct_python_tuple)

    def loadyaml(self, filename):
        yamldata = None
        with open(self._definitions_directory + '/' + filename, 'r') as stream:
            try:
                yamldata = self.yaml.load(stream)
        #        print(dump(t, default_flow_style=False))
        #        print type(t)
            except YAMLError as exc:
                print(exc)

        if not yamldata:
            print(yamldata)
            raise ValueError("Failed to parse YAML Data")
        return yamldata

    def dumpyaml(self, data, filename):

        with open(self._definitions_directory + '/' + filename, 'w') as stream:
            dump(data, stream, default_flow_style=False)
