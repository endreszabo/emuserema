
from emuserema.services import RDPservice
from emuserema.plugin_manager import Plugin
from emuserema.utils import makedir_getfd, cleanup_dir


class RDPTreeRenderer(Plugin):
    def config(self):
        self.description = 'mstsc.exe ".rdp" profile files renderer'

    def cleanup(self):
        cleanup_dir(self._config['output_dir'])

    def render_rdp(self):
        for key, service in self.services.items():
            if isinstance(service, RDPservice):
                with makedir_getfd("%s/%s.rdp" % (self._config['output_dir'], '/'.join(service.path))) as dst:
                    for key, value in service.kwargs.items():
                        if key[0] != '_':
                            print("%s:%s" % (key, value), file=dst)

    def run(self, **kwargs):
        self.services = kwargs['services']
        self.worlds = kwargs['worlds']
        self.render_rdp()
