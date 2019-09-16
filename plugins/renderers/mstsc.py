
from services import RDPservice
from plugin_manager import Plugin

class JsTreeRenderer(Plugin):
    def config(self):
        self.description = 'mstsc.exe ".rdp" profile files renderer'

    def render_rdp(self):
        tree=[]
        for key, service in self.services.items():
            if isinstance(service, RDPservice):
                with open("output/RDP/%s.rdp" % ('/'.join(service.path)), 'w') as dst:
                    for key, value in service.kwargs.items():
                        if key[0]!='_':
                            print("%s:%s" % (key, value), file=dst)

    def run(self, **kwargs):
        self.services=kwargs['services']
        self.worlds=kwargs['worlds']
        self.render_rdp()
