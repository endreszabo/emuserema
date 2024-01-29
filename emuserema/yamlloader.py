#import ruamel.yaml

#from ruamel.std.pathlib import Path
#from ruamel.yaml import YAML, version_info, dump, YAMLError, SafeLoader, RoundTripLoader
#from ruamel.yaml import YAML, YAMLError, dump, SafeLoader
import ruamel.yaml
from os.path import isfile, splitext, isdir
from jinja2 import ChoiceLoader, PackageLoader, FileSystemLoader, Environment
from os import environ, uname, listdir, access, X_OK
from subprocess import check_output
from toml import loads as toml_loads
from json import loads as json_loads
from csv import DictReader
from io import StringIO
import re
import logging

log = logging.getLogger(__name__)


kv_regex = re.compile('^\s*([a-zA-Z_.]+)[\t :=]+(.*)')

def csv_loads(s: str) -> dict:
    """A simple interface to csvloader

    Args:
        s (str): Input file as a string

    Returns:
        str: Parsed CSV as dict
    """

    reader = DictReader(s.split("\n"))
    rv={}
    for row in reader:
        #field with name 'nodename' is the dict key
        rv[row.pop('nodename')] = row
    return rv

def get_file_or_exec_contents(path: str) -> str:
    """gets file contents or executes it for its stdout
    if file is executable

    Args:
        path (str): path to file or executable

    Returns:
        str: contents of file or stdout of executable ran
    """
    if access(path, X_OK):
        log.debug("file '%s' is executable, it will be executed and its output processed as file extensions suggests" % path)
        return check_output(args=[path], shell=False).decode('utf-8')
    with open(path, 'r') as infile:
        return infile.read()

class EmuseremaRelativeSafeLoader(ruamel.yaml.SafeLoader):
    def __init__(self, definitions_directory= None):
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
        path = node.value
        if isfile(self._definitions_directory + '/' + path + '.j2'):
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
        with open(self._definitions_directory + '/' + path, 'r') as infile:
            if ruamel.yaml.version_info < (0, 15):
                #yaml.composer.anchors = cons.composer.anchors
                return ruamel.yaml.safe_load(infile)
            else:
                y = cons.loader
                yaml = ruamel.yaml.YAML(typ=y.typ, pure=y.pure)
                yaml.composer.anchors = cons.composer.anchors
                return yaml.load(infile)
    

    def file_to_dict(self, yaml_cons, path):
        name, ext = splitext(path)
        rv = {}
        if ext == '.toml':
            log.debug('loading TOML format data from file %r' % path)
            return toml_loads(s = get_file_or_exec_contents(path=path))
        elif ext == '.json':
            log.debug('loading JSON format data from file %r' % path)
            return json_loads(s = get_file_or_exec_contents(path=path))
        elif ext == '.yaml':
            log.debug('loading YAML format data from file %r' % path)
            y = yaml_cons.loader
            yaml = ruamel.yaml.YAML(typ=y.typ, pure=y.pure)
            yaml.composer.anchors = yaml_cons.composer.anchors
            return yaml.load(get_file_or_exec_contents(path=path))
        elif ext == '.csv':
            log.debug('loading CSV format data from file %r' % path)
            return csv_loads(s = get_file_or_exec_contents(path=path))
        else:
            log.warning("extension of file '%s' is unknown and will be read as a simple key-value store" % path)
            with open(path, 'r') as file:
                for index, line in enumerate(file):
                    match = kv_regex.match(line)
                    if (match):
                        group = match.groups()
                        if len(group) == 2:
                            rv[group[0]] = group[1]
                        else:
                            log.debug("simple key-value store entry in file '%s', line #%d did not match expected kv-regex: %r" % (path, index, line))
                    else:
                        log.debug("simple key-value store entry in file '%s', line #%d did not match expected kv-regex: %r" % (path, index, line))
                return rv

    def file_include(self, cons, node):
        path = node.value
        if isdir(path):
            rv = {}
            for item in listdir(path):
                if isfile(path + '/' + item):
                    name, ext = splitext(item)
                    rv[name] = self.file_to_dict(cons, path + '/' + item)
                elif isdir(path):
                    log.debug("file_include() recursively descends into directory %r", path+'/'+item)
                    node.value = path + '/' + item
                    rv[item] = self.file_include(cons, node)
            return rv
        else:
            return self.file_to_dict(cons, path + '/' + item)

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
            self.yaml.add_constructor('!includedir', loader.file_include)
            self.yaml.add_constructor('tag:yaml.org,2002:python/tuple', loader.construct_python_tuple)
        else:
            self.yaml.Constructor.add_constructor('!include', loader.yaml_include)
            self.yaml.Constructor.add_constructor('!includedir', loader.file_include)
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
                except ruamel.yaml.YAMLError as exc:
                    print(exc)

        if not yamldata:
            raise ValueError("Failed to parse YAML Data")
        return yamldata

    def dumpyaml(self, data, filename):

        with open(self._definitions_directory + '/' + filename, 'w') as stream:
            ruamel.yaml.dump(data, stream, default_flow_style=False)
