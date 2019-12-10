from emuserema.services import SSHservice
from emuserema.plugin_manager import Plugin
from emuserema.utils import makedir_getfd


class WsshCommandsRenderer(Plugin):
    """This plugin is just the identity function: it returns the argument
    """
    def config(self):
        self.description = 'wssh launcher framework commands generator'

    def render_commands(self):
        with makedir_getfd(self._config['output_file']) as dmenu:
            print(self.render_kv(), file=dmenu)

    def render_kv(self):
        rv = []
        for key, service in self.services.items():
            #service=self.services[key]
            if isinstance(service, SSHservice):
                if ('_gui' not in service.kwargs or service.kwargs['_gui'] is True):
                    rv.append("%s%s" % (
                        '/'.join(service.path[1:]),
                        service.label)
                    )
        return("\n".join(rv))

    def run(self, **kwargs):
        """The actual implementation of the identity plugin is to just return the
        argument
        """
        self.services = kwargs['services']
        self.worlds = kwargs['worlds']
        self.render_commands()
