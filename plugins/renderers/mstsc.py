
from services import RDPservice
from plugin_manager import Plugin
from os import walk, path, rmdir, makedirs
from shutil import rmtree

class RDPTreeRenderer(Plugin):
    def config(self):
        self.description = 'mstsc.exe ".rdp" profile files renderer'

    def clean_tree(self):
        for root, dirs, files in walk('output/RDP/', topdown=False):
            for name in dirs:
                try:
                    rmtree(path.join(root, name))
                except OSError as e:
                    print("Ran into an exception during removal of %s: '%s'" % (path.join(root, name), e))

    def render_rdp(self):
        tree=[]
        for key, service in self.services.items():
            if isinstance(service, RDPservice):
                path='output/RDP/%s' % '/'.join(service.path[:-1])
                makedirs(path, exist_ok=True)
                with open("%s/%s.rdp" % (path, service.path[-1]), 'w') as dst:
                    for key, value in service.kwargs.items():
                        if key[0]!='_':
                            print("%s:%s" % (key, value), file=dst)

    def run(self, **kwargs):
        self.services=kwargs['services']
        self.worlds=kwargs['worlds']
        self.render_rdp()
