from emuserema.services import SSHservice
from emuserema.plugin_manager import Plugin
from emuserema.utils import makedir_getfd


class PuttyRenderer(Plugin):
    def config(self):
        self.description = 'PuTTY registry generator'
        self.registries = {}

    def render_putty(self):
        for key, service in self.services.items():
            if isinstance(service, SSHservice):
                putty_config = self.open_registry(service.path[0])
                print("[HKEY_CURRENT_USER\\Software\\SimonTatham\\PuTTY\\Sessions\\%s]" %
                    service.tag, file=putty_config)
                for k, v in self.render_kv(service):
                    print("\"%s\"=%s" % (k, v), file=putty_config)
                print('', file=putty_config)
        self.close_registries()

    def render_kv(self, service):
        rv = []
        for key, value in service.kwargs.items():
            if key[0] == '_':  # Blindly copy all the non meta settings
                continue
            key = key.lower()
            if key == 'user':
                rv.append(('UserName', '"%s"' % value))
            elif key == 'port':
                rv.append(('PortNumber', 'dword:%08x' % value))
        port_forwardings = []
        if service.forwards['local']:
            #print(service.forwards['local'])
            port_forwardings += map(lambda x: "L" + x[0] + "=" + x[1][0], service.forwards['local'].items())
        if service.forwards['remote']:
            port_forwardings += map(lambda x: "R" + x[0] + "=" + x[1][0], service.forwards['remote'].items())
        if service.forwards['dynamic']:
            port_forwardings += map(lambda x: "D" + x, service.forwards['dynamic'])
        rv.append(('PortForwardings', '"' + ','.join(port_forwardings) + '"'))
        for k, v in service.putty_settings:
            rv.append((k, v))
        return rv

    def open_registry(self, world_name):
        if world_name not in self.registries:
            self.registries[world_name] = makedir_getfd("%s/%s.reg" % (self._config['output_dir'], world_name))
            print("Windows Registry Editor Version 5.00\n", file=self.registries[world_name])
            print("[HKEY_CURRENT_USER\\Software\\SimonTatham\\PuTTY\\Sessions]\n", file=self.registries[world_name])

        return self.registries[world_name]

    def close_registries(self):
        for key, registry in self.registries.items():
            registry.close()

    def run(self, **kwargs):
        self.services = kwargs['services']
        self.worlds = kwargs['worlds']
        self.render_putty()
