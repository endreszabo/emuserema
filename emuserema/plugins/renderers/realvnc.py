from emuserema.plugin_manager import Plugin
from emuserema.services import VNCservice
from emuserema.utils import makedir_getfd

# for RealVNC session file UUID creation
from uuid import UUID, uuid5
vnc_namespace = UUID('d1982572-cbf4-5bdc-b52e-a03c843e2f4d')


class RealVNCRenderer(Plugin):
    def config(self):
        self.description = 'RealVNC profile files renderer'

    def render_realvnc(self):
        for key, service in self.services.items():
            if isinstance(service, VNCservice):
                uuid = uuid5(vnc_namespace, service.tag)
                service.kwargs['Uuid'] = uuid
                if 'FriendlyName' not in service.kwargs:
                    service.kwargs['FriendlyName'] = service.tag
                with makedir_getfd('%s/%s' % (self._config['output_dir'], str(uuid))) as dst:
                    for key, value in service.kwargs.items():
                        if key[0] != '_':
                            print("%s=%s" % (key, value or ''), file=dst)

    def run(self, **kwargs):
        """The actual implementation of the identity plugin is to just return the
        argument
        """
        self.services = kwargs['services']
        self.worlds = kwargs['worlds']
        self.render_realvnc()
