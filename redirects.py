from yamlloader import loadyaml, dump

DB_FILE='lib/redirects.yaml'

class RedirectFactory:
    def __init__(self):
        self.db = loadyaml(DB_FILE)
        if 'counter' not in self.db:
            self.db['counter']=38000
        if 'bindip' not in self.db:
            self.db['bindip']='44.128.191.10'
        if 'redirects' not in self.db:
            self.db['redirects']={}

    def allocate(self, via_service, target_service):
        if((via_service.tag, target_service.tag) not in self.db['redirects']):
            self.db['redirects'][(via_service.tag,target_service.tag)]=(self.db['bindip'],self.db['counter'])
            self.db['counter']+=1
        return self.db['redirects'][(via_service.tag,target_service.tag)]

    def commit(self):
        with open(DB_FILE,'w') as counter_fd:
            dump(self.db, counter_fd)

