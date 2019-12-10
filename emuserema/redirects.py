DB_FILE = '.redirects.yaml'


class RedirectFactory:
    def __init__(self, yamlloader=None, definitions_directory=None):
        self._definitions_directory = definitions_directory
        self._db_path = DB_FILE
        self._yamlloader = yamlloader
        self.db = self._yamlloader.loadyaml(self._db_path)
        if 'counter' not in self.db:
            self.db['counter'] = 38000
        if 'bindip' not in self.db:
            self.db['bindip'] = '44.128.191.10'
        if 'redirects' not in self.db:
            self.db['redirects'] = {}

    def allocate(self, via_service, target_service):
        if((via_service.tag, target_service.tag) not in self.db['redirects']):
            self.db['redirects'][(via_service.tag, target_service.tag)] = (self.db['bindip'], self.db['counter'])
            self.db['counter'] += 1
        return self.db['redirects'][(via_service.tag, target_service.tag)]

    def commit(self):
        self._yamlloader.dumpyaml(self.db, DB_FILE)

