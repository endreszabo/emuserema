from emuserema.services import URLservice
from emuserema.plugin_manager import Plugin
from emuserema.utils import service_paths_to_tree, makedir_getfd
import json


class JsTreeRenderer(Plugin):
    def config(self):
        self.description = 'jstree URL launcher site renderer'

    def render_jstree(self, world):
        #tree=[]
        tree = []
        lst = []

        for service in world.services.values():
            if isinstance(service, URLservice):
                lst.append((service.path[1:], service))
        tree = service_paths_to_tree(lst)
        if tree:

            with makedir_getfd("%s/%s.html" % (self._config['output_dir'], world.name)) as dst:
                try:
                    with open('templates/jstree-html-prefix.html', 'r') as preamble:
                        for line in preamble:
                            dst.write(line)
                except FileNotFoundError:
                    pass

                json.dump(obj=tree, fp=dst, sort_keys=True, indent=2)

                try:
                    with open('templates/jstree-html-postfix.html', 'r') as preamble:
                        for line in preamble:
                            dst.write(line)
                except FileNotFoundError:
                    pass

    def run(self, **kwargs):
        """The actual implementation of the identity plugin is to just return the
        argument
        """
        self.services = kwargs['services']
        self.worlds = kwargs['worlds']
        for world in self.worlds:
            self.render_jstree(self.worlds[world])
