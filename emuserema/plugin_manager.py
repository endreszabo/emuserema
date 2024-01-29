# This section is mostly based on works of Guido Diepen as seen at
# https://www.guidodiepen.nl/2019/02/implementing-a-simple-plugin-framework-in-python/

import pkgutil
import os
import inspect


class Plugin(object):
    def __init__(self, config={}):
        self.description = 'UNKNOWN'
        self._config = config
        self.worlds = {}
        self.services = {}
        self.config()
        if 'cleanup' in self._config and self._config['cleanup'] is True:
            self.cleanup()

    def cleanup(self):
        raise NotImplementedError

    def config(self):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError

    def run(self, **kwargs):
        self.services = kwargs['services']
        self.worlds = kwargs['worlds']
        self.render()


class PluginManager(object):
    def __init__(self, plugin_package, config):
        self.plugin_package = plugin_package
        self.config = config
        self.reload_plugins()

    def reload_plugins(self):
        self.plugins = []
        self.seen_paths = []
        self.walk_package(self.plugin_package)

    def run_all(self, kwargs):
        rv = []
        for plugin in self.plugins:
            rv.append(plugin.run(**kwargs))
        return rv

    def run_selected(self, enabled_plugins, **kwargs):
        rv = []
        enabled_plugins = list(enabled_plugins)
        for plugin in self.plugins:
            if plugin.__class__.__module__.split('.')[-1] in enabled_plugins:
                rv.append(plugin.run(**kwargs))
        return rv

    def walk_package(self, package):
        imported_package = __import__(package, fromlist=['blah'])

        for _, pluginname, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not ispkg:
                plugin_module = __import__(pluginname, fromlist=['blah'])
                clsmembers = inspect.getmembers(plugin_module, inspect.isclass)
                for (_, c) in clsmembers:
                    if issubclass(c, Plugin) & (c is not Plugin):
                        self.plugins.append(c(config=self.config[pluginname.split('.')[-1]] or {}))
            all_current_paths = []
            if isinstance(imported_package.__path__, str):
                all_current_paths.append(imported_package.__path__)
            else:
                all_current_paths.extend([x for x in imported_package.__path__])

            for pkg_path in all_current_paths:
                if pkg_path not in self.seen_paths:
                    self.seen_paths.append(pkg_path)

                    child_pkgs = [p for p in os.listdir(pkg_path) if os.path.isdir(os.path.join(pkg_path, p))]

                    for child_pkg in child_pkgs:
                        self.walk_package(package + '.' + child_pkg)
