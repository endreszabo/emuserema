
from emuserema.services import SSHservice
from emuserema.plugin_manager import Plugin
from emuserema.utils import makedir_getfd, cleanup_files


class OpenSSHRenderer(Plugin):
    def config(self):
        self.description = 'openssh client configuration files renderer'
        self.ssh_config_files = {}

    def cleanup(self):
        cleanup_files(self._config['output_dir'])

    def render_openssh(self):
        for key, service in self.services.items():
            #service=self.services[key]
            if isinstance(service, SSHservice):
                ssh_config_file = self.open_ssh_config_file(service.world)
                print("\n###\n### %s\n###\n" % service.tag, file=ssh_config_file)
                print("Host %s" % service.tag, file=ssh_config_file)
                print("\n".join(service.pb), file=ssh_config_file)
                #for k in self.render_kv(service):
                #    if type(k) == tuple:
                #        print("\t%s = %s" % (k[0], k[1]), file=ssh_config_file)
                #    elif type(k) == str:
                #        print("\t"+k, file=ssh_config_file)

        self.close_ssh_config_files()

    def render_kv(self, service):
        rv = []
        for key, value in service.kwargs.items():
            if key[0] != '_':  # Blindly copy all the non meta settings
                rv.append((key, value))
        for bind_hostport, target_hostport in service.forwards['local'].items():
            if target_hostport[1]:
                rv.append('#' + target_hostport[1])
            rv.append(('LocalForward', "%s %s" % (bind_hostport, target_hostport[0])))
        for bind_hostport, target_hostport in service.forwards['remote']:
            if target_hostport[1]:
                rv.append('#' + target_hostport[1])
                rv.append(('RemoteForward', "%s %s" % (bind_hostport, target_hostport[0])))
        for bind_hostport in service.forwards['dynamic']:
            if target_hostport[1]:
                rv.append('#' + target_hostport[1])
                rv.append(('DynamicForward', "%s" % (bind_hostport, target_hostport[0])))
        return rv

    def open_ssh_config_file(self, world_name):
        if world_name not in self.ssh_config_files:
            self.ssh_config_files[world_name] = makedir_getfd("%s/%s" % (self._config['output_dir'], world_name))
            try:
                with open('templates/ssh_config_prefix', 'r') as preamble:
                    for line in preamble:
                        self.ssh_config_files[world_name].write(line)
            except FileNotFoundError:
                pass

        return self.ssh_config_files[world_name]

    def close_ssh_config_files(self):
        for key, ssh_config_file in self.ssh_config_files.items():
            try:
                with open('templates/ssh_config_postfix', 'r') as postfix:
                    for line in postfix:
                        ssh_config_file.write(line)
            except FileNotFoundError:
                pass
            ssh_config_file.close()

    def run(self, **kwargs):
        self.services = kwargs['services']
        self.worlds = kwargs['worlds']
        self.render_openssh()
