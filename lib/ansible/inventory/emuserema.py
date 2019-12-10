#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Endre Szabo
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
    name: emuserema
    plugin_type: inventory
    short_description: EMUSEREMA inventory source
    description:
        - Builds inventory from specific EMUSEREMA worlds
    extends_documentation_fragment:
      - constructed
    version_added: 2.9.2
    author: Endre Szabo (@endreszabo)
    options:
        world:
            description: EMUSEREMA world name to render
            required: true
    requierements: a working EMUSEREMA environment
    seealso:
      - name: EMUSEREMA project homepage
        description: EMUSEREMA project homepage with extensive documentations and examples.
        link: https://end.re/emuserema/
'''

EXAMPLES = r'''
---
plugin: emuserema
world: home
'''

#from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from sys import path

from emuserema import Emuserema

class InventoryModule(BaseInventoryPlugin, Constructable):
    ''' Host inventory parser for ansible using native EMUSEREMA. '''

    NAME = 'emuserema'

    def __init__(self):
        super(InventoryModule, self).__init__()

    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith('emuserema.yaml'):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):

        super(InventoryModule, self).parse(inventory, loader, path)

        config_data = self._read_config_data(path)

        # set _options from config data
        self._consume_options(config_data)

        self.emuserema = Emuserema()

        return self.emuserema.populate_ansible_inventory(inventory=inventory, world=self.get_option('world'))
