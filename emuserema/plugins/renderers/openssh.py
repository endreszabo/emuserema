"""OpenSSH renderer"""

from jinja2 import ChoiceLoader, PackageLoader, FileSystemLoader, Environment
from emuserema.services import SSHservice
from emuserema.plugin_manager import Plugin
from emuserema.utils import makedir_getfd, cleanup_files


class OpenSSHRenderer(Plugin):
    def config(self):
        self.description = 'openssh client configuration files renderer'
        self.ssh_config_files = {}
        self.jinja_env = Environment(loader=ChoiceLoader([
            PackageLoader('emuserema'),
            FileSystemLoader(searchpath='templates', followlinks=True)
        ]))
        self.template = self.jinja_env.get_template('openssh/openssh.j2')

    def cleanup(self):
        cleanup_files(self._config['output_dir'])

    def render_openssh(self):
        for world in self.worlds:
            with makedir_getfd("%s/%s" % (self._config['output_dir'], self.worlds[world].name)) as ssh_config_file:
                print(
                    self.template.render(
                        services=list(map(
                            lambda service: self.worlds[world].services[service],
                            filter(
                                lambda service: isinstance(self.worlds[world].services[service], SSHservice),
                                list(self.worlds[world].services.keys())
                            )
                        )),
                        world=self.worlds[world]
                    ),
                    file=ssh_config_file
                )

    def run(self, **kwargs):
        self.services = kwargs['services']
        self.worlds = kwargs['worlds']
        self.render_openssh()
