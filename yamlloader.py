import ruamel.yaml

import sys
#from ruamel.std.pathlib import Path
from ruamel.yaml import YAML, version_info, dump, YAMLError, SafeLoader, RoundTripLoader

yaml = YAML(typ='safe', pure=True)
yaml.default_flow_style = False

def my_compose_document(self):
    self.parser.get_event()
    node = self.compose_node(None, None)
    self.parser.get_event()
    # self.anchors = {}    # <<<< commented out
    return node

yaml.Composer.compose_document = my_compose_document

class PrettySafeLoader(SafeLoader):
    def construct_python_tuple(self, node):
        return tuple(self.construct_sequence(node))
    # adapted from http://code.activestate.com/recipes/577613-yaml-include-support/
    def yaml_include(loader, node):
        y = loader.loader
        yaml = YAML(typ=y.typ, pure=y.pure)  # same values as including YAML
        yaml.composer.anchors = loader.composer.anchors
        with open(node.value,'r') as infile:
            return yaml.load(infile)

yaml.Constructor.add_constructor('!include', PrettySafeLoader.yaml_include)
yaml.Constructor.add_constructor('tag:yaml.org,2002:python/tuple', PrettySafeLoader.construct_python_tuple)

def loadyaml(filename):
    yamldata = None
    with open(filename, 'r') as stream:
        try:
            yamldata=yaml.load(stream)
    #        print(dump(t, default_flow_style=False))
    #        print type(t)
        except YAMLError as exc:
            print(exc)

    if not yamldata:
        print(yamldata)
        raise ValueError("Failed to parse YAML Data")
    return yamldata 

