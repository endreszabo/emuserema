from emuserema.services import *

class World(object):
    """ Obsolete class, only one renderer uses it """
    def __init__(self, name):
        self.name = name
        self.redirects=[]
        self.services={}
        self.tree={}
        self.service_index={}

    def append(self, service):
        self.services[service.tag] = service

    def render(self):
        pass

    def __repr__(self):
        return "<World '%s'>" % self.name

def __str__(self):
    return self.name

def append_redirect(self, via_service, target_service):
    self.redirects.append(self.redirect_factory.allocate(via_service, target_service))
    pass
