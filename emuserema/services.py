
USE_PANGO_TAGS=1
STAGE3_PATH='~/bin/emuserema-ssh-wrapper.sh'
from abc import ABCMeta, abstractmethod

#FOR URLservice support:
from urllib.parse import urlparse
from emuserema.utils import get_ansible_treevars, inherit, y7address

ABC = ABCMeta('ABC', (object,), {'__slots__': ()})

import logging
log = logging.getLogger(__name__)

class AbstractService(ABC):
    def __init__(self, path=[], kwargs={}, treevars=[]):
        self.pb = []
        self.tag = path[-1]
        self.world = path[0]
        self.path = path
        self.kwargs = kwargs
        #self.label="%s\t" % tag
        self.label = ""
        self.via = None
        self.treevars = treevars

        self.config()

    @abstractmethod
    def config(self):
        raise NotImplementedError

    @abstractmethod
    def process_proxy(self, via_service, redirect_factory):
        raise NotImplementedError

    def get(self, key):
        return(self.kwargs.get(key))

    def __repr__(self):
        return("<{}({!r})>".format(self.__class__.__name__, self.tag))


class DummyService(AbstractService):
    def __init__(self, path=[], kwargs={}, treevars=[]):
        self.pb = []
        self.tag = path[-1]
        self.world = path[0]
        self.path = path
        self.kwargs = kwargs
        #self.label="%s\t" % tag
        self.label = ""
        self.via = None
        self.treevars = treevars

        self.config()

    def config(self):
        if 'domain_item' in self.treevars and self.tag[-1] != '.':
            self.tag = ".".join([self.tag] + self.treevars['domain_item'])
        pass

    def process_proxy(self, via_service, redirect_factory):
        pass

    def __repr__(self):
        return("<{}({!r})>".format(self.__class__.__name__, self.tag))


class SSHserviceAttribute(object):
    def __init__(self, key, value, comment):
        self.key=key
        self.value=value
        self.comment=comment


class SSHservice(AbstractService):

    #This is to support redirection of hosts that are SCB monitored and behind restricted SSH terminal server gateways
    @property
    def world(self):
        if self.via and not isinstance(self.via, SSHoverSCBservice):
            return self.via.world
        return self._world

    @property
    def realworld(self):
        return self._world

    @world.setter
    def world(self, world):
        self._world=world

    def config(self):
        self.putty_settings=[]
        self.forwards={
            'local': {},
            'remote': {},
            'dynamic': {}
        }

        if 'domain_item' in self.treevars and self.tag[-1]!='.':
            self.tag = ".".join([self.tag]+self.treevars['domain_item'])

        #IP address or hostname was not specified in YAML, we add one
        if 'hostname' not in map(lambda x: x.lower(), self.kwargs.keys()):
            if 'site_id' in self.treevars and '_ipoffset' in self.kwargs:
                log.debug("adding default hostname for y7 host %r" % self.tag)
                self.kwargs['HostName'] = y7address(self.treevars['site_id'][0], self.kwargs['_ipoffset'], 6)
            else:
                log.debug("adding default HostName entry for SSHservice %r" % self.tag)
                self.kwargs['HostName'] = self.tag
        for key, value in self.kwargs.items():
            if key[0]!='_': #Blindly copy all the non meta settings
                self.pb.append("\t%s = %s" % (key, self.kwargs[key]))
            else:
                key=key.lower()
                if key == '_via':
                    #non relative FQDN
                    if value[-1]=='.':
                        self.via = value[:-1]
                    #a relative host in our subdomain
                    elif 'domain_item' in self.treevars:
                        self.via = ".".join([value]+self.treevars['domain_item'])
                    else:
                        raise NotImplementedError('Unknown via host', self.path, self.tag, value, self.treevars)

                elif key == '_forward':
                    #print self.kwargs[key]
                    if 'local' in self.kwargs[key]:
                        for bind_hostport, target_hostport in self.kwargs[key]['local'].items():
                            self.add_local_forward(bind_hostport, target_hostport, comment="added from YAML")
                            self.pb.append('\tLocalForward = %s %s' % (bind_hostport, target_hostport))
                    if 'remote' in self.kwargs[key]:
                        for bind_hostport, target_hostport in self.kwargs[key]['remote'].items():
                            self.add_remote_forward(bind_hostport, target_hostport, comment="added from YAML")
                            self.pb.append('\tRemoteForward = %s %s' % (bind_hostport, target_hostport))
                    if 'dynamic' in self.kwargs[key]:
                        for bind_hostport in self.kwargs[key]['dynamic']:
                            self.add_dynamic_forward(bind_hostport, target_hostport, comment="added from YAML")
                            self.pb.append('\tDynamicForward = %s %s' % (bind_hostport))
                elif key == '_hostkeyalias':
                    self.pb.append('\tHostKeyAlias = %s' % (self.tag))
        self.add_label()

    def add_label(self):
        if '_terminal' not in self.kwargs:
            #self.label="%s" % self.tag
            if USE_PANGO_TAGS:
                self.label+=" <span font_size='x-small' fgcolor='#a0a080'>as %s</span>" % (self.kwargs['User'])
            self.label+="\turxvtc -tn rxvt-unicode -T \"SSH: %s@%s\" -insecure -e %s %s %s" % (self.kwargs['User'], self.tag, STAGE3_PATH, self.tag, self.tag)
        pass

    def process_proxy(self, via_service, redirect_factory):
        if type(via_service) == SSHservice:
            self.pb.append('\tProxyCommand = ssh -oLogLevel=QUIET -F ~/.ssh/configs/{0} -W \'[%h]\':%p {1}'.format(via_service.world, via_service.tag))
            ##print(self.kwargs.keys())
            self.putty_settings.append(("ProxyTelnetCommand",'"plink %s -nc %s:%s\\n"' % (via_service.tag, self.kwargs['HostName'], self.kwargs['Port'])))
            #if type(via_service) == SSHoverSCBservice:
            #    self.world = via_service.tag
        elif type(via_service) == SSHoverSCBservice:
            self.world = via_service.tag
            self.label = ''
            if USE_PANGO_TAGS:
                self.label+=" <span font_size='x-small' fgcolor='#a0a080'>as %s</span>" % (self.kwargs['User'])
                self.label+=" <span font_size='xx-small' font_style='italic' fgcolor='#a0a080'>(via %s)</span>" % (via_service.tag)
            self.label+="\turxvtc -tn rxvt-unicode -T \"SSH: %s@%s via %s\" -insecure -xrm \"urxvt.answerbackString: clear;exec /usr/bin/ssh -F ~/.ssh/configs/%s %s\\\\n\" -e %s %s %s" % (self.kwargs['User'], self.tag, via_service.tag, via_service.tag, self.tag, STAGE3_PATH, via_service.tag, self.tag)
            self.putty_settings.append(("HostName",'"%s"'% via_service.tag))
            self.putty_settings.append(("Answerback",'"clear;exec /usr/bin/ssh -F ~/.ssh/configs/%s %s^M"' % (via_service.tag, self.tag)))
            #self.putty_settings.append(("ProxyTelnetCommand",'"plink %s -nc %s:%s\\n"' % (via_service.tag, self.kwargs['HostName'], self.kwargs['Port'])))

    def add_local_forward(self, bind_hostport, target_hostport, comment=None):
        self.forwards['local'][bind_hostport]=(target_hostport, comment)

    def add_remote_forward(self, bind_host, bind_port, target_host, target_port, comment=None):
        self.forwards['remote'][bind_hostport]=(target_hostport, comment)

    def add_dynamic_forward(self, bind_host, bind_port, target_host, target_port, comment=None):
        self.forwards['dynamic'][bind_hostport]=comment


class SSHoverSCBservice(SSHservice):
    pass


class URLservice(AbstractService):
    def config(self):
        if '_via' in self.kwargs:
            value = self.kwargs['_via']
            #non relative FQDN
            if value[-1]=='.':
                self.via = value[:-1]
            #a relative host in our subdomain
            elif 'domain_item' in self.treevars:
                self.via = ".".join([value]+self.treevars['domain_item'])
            else:
                raise NotImplementedError('Unknown via host', value, self.tag)
        self.url = self.kwargs['url']
        self.original_url = self.kwargs['url']

    def process_proxy(self, via_service, redirect_factory):
        purl = urlparse(self.url)
        (bindip, bindport) = redirect_factory.allocate(via_service, self)
        dport = purl.port

        if dport is None:
            if purl.scheme == 'http':
                dport = 80
            elif purl.scheme == 'https':
                dport = 443
            else:
                raise NotImplementedError("URL scheme '%s' is not supported" % purl.scheme)

        via_service.pb.append('\t# EMUSEREMA added implicit redirection for service "%s" at URL: %s' % (self.tag, self.url) )
        via_service.pb.append('\tLocalForward = %s:%s %s' % (bindip, bindport, "%s:%s" % (purl.hostname, dport)))
        via_service.add_local_forward("%s:%s" % (bindip, bindport), "%s:%s" % (purl.hostname, dport), '# EMUSEREMA added implicit redirection for service "%s" at URL: %s' % (self.tag, self.url))

        self.original_url = self.url
        self.url = purl._replace(netloc = '%s:%s' % (bindip, bindport)).geturl()


class RDPservice(AbstractService):
    def config(self):
        if '_via' in self.kwargs:
            value = self.kwargs['_via']
            #non relative FQDN
            if value[-1]=='.':
                self.via = value[:-1]
            #a relative host in our subdomain
            elif 'domain_item' in self.treevars:
                self.via = ".".join([value]+self.treevars['domain_item'])
            else:
                raise NotImplementedError('Unknown via host', value, self.tag)

    def process_proxy(self, via_service, redirect_factory):
        self._original_full_address=self.kwargs["full address"]
        (bindip, bindport) = redirect_factory.allocate(via_service, self)
        via_service.pb.append('\t# EMUSEREMA added implicit redirection for RDP service "%s" at listening address: %s' % (self.tag, self._original_full_address))
        via_service.pb.append('\tLocalForward = %s:%s %s' % (bindip, bindport, "%s" % (self._original_full_address[2:])))
        self.kwargs["full address"] = "s:%s:%s" % (bindip, bindport)


class VNCservice(AbstractService):
    def config(self):
        if '_via' in self.kwargs:
            value = self.kwargs['_via']
            #non relative FQDN
            if value[-1]=='.':
                self.via = value[:-1]
            #a relative host in our subdomain
            elif 'domain_item' in self.treevars:
                self.via = ".".join([value]+self.treevars['domain_item'])
            else:
                raise NotImplementedError('Unknown via host', value, self.tag)

    def process_proxy(self, via_service, redirect_factory):
        bindip, bindport = redirect_factory.allocate(via_service, self)

        try:  # Direct port definition
            self.kwargs['Host'].index('::')
            targetip, targetport = self.kwargs['Host'].split('::')
        except ValueError:  # VNC display offset definition
            try:
                self.kwargs['Host'].index(':')
                targetip, targetport = self.kwargs['Host'].split(':')
                targetport = int(targetport) + 5900
            except ValueError:  # Fallback to port 5900 when no port or display number specified
                targetip = self.kwargs['Host']
                targetport = 5900

        via_service.pb.append('\t# EMUSEREMA added implicit redirection for VNC service "%s" at listening address: %s' % (self.tag, self.kwargs['Host']) )
        self.original_host = self.kwargs['Host']
        via_service.pb.append('\tLocalForward = %s %s:%s' % (self.kwargs['Host'], targetip, targetport))
        self.kwargs['Host'] = '%s:%s' % (bindip, bindport)


class ServiceFactory(object):
    def __init__(self):
        self.builders={
            'ssh': SSHservice,
            'ssh_over_scb': SSHoverSCBservice,
            'url': URLservice,
            'dummy': DummyService,
            'rdp': RDPservice,
            'vnc': VNCservice
        }

    def create(self, path, kwargs, emuserema):
        treevars = inherit(get_ansible_treevars(emuserema.data, path))
        return self.builders[kwargs['_type']](
                        path = path,
                        kwargs = kwargs,
                        treevars = treevars
                    )

    def supported(self, obj):
        return obj['_type'] in self.builders.keys()

