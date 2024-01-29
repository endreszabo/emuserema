"""OpenSSH renderer"""

from jinja2 import ChoiceLoader, PackageLoader, FileSystemLoader, Environment
from emuserema.services import SSHservice
from emuserema.plugin_manager import Plugin
from emuserema.utils import makedir_getfd, cleanup_files


class OpenSSHRenderer(Plugin):
    """Plugin class that render SSH configurations"""
    def config(self):
        self.description = 'openssh client configuration files renderer'
        self.ssh_config_files = {}
        self.jinja_env = Environment(loader=ChoiceLoader([
            PackageLoader('emuserema'),
            FileSystemLoader(searchpath='templates', followlinks=True)
        ]))
        self.template = self.jinja_env.get_template('openssh/openssh.j2')

    def cleanup(self):
        """Removes all files from the destination directories"""
        cleanup_files(self._config['output_dir'])

    def render(self):
        """Actual function that renders the jinja templates"""
        for world in self.worlds:
            with makedir_getfd("%s/%s" % (self._config['output_dir'],
                    self.worlds[world].name)) as ssh_config_file:
                print(
                    self.template.render(
                        services=list(map(
                            lambda service, w=world: self.worlds[w].services[service],
                            filter(
                                lambda service, w=world:
                                    isinstance(self.worlds[w].services[service], SSHservice),
                                list(self.worlds[world].services.keys())
                            )
                        )),
                        world=self.worlds[world]
                    ),
                    file=ssh_config_file
                )
