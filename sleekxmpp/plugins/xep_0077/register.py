"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import logging

import sleekxmpp
from sleekxmpp.stanza import StreamFeatures, Iq
from sleekxmpp.xmlstream import register_stanza_plugin, JID
from sleekxmpp.plugins.base import BasePlugin, register_plugin
from sleekxmpp.plugins.xep_0077 import stanza, Register, RegisterFeature


log = logging.getLogger(__name__)


class XEP_0077(BasePlugin):

    """
    XEP-0077: In-Band Registration
    """

    name = 'xep_0077'
    description = 'XEP-0077: In-Band Registration'
    dependencies = set(['xep_0004', 'xep_0066'])
    stanza = stanza

    def plugin_init(self):
        self.create_account = self.config.get('create_account', True)

        register_stanza_plugin(StreamFeatures, RegisterFeature)
        register_stanza_plugin(Iq, Register)

        if self.xmpp.is_component:
            pass
        else:
            self.xmpp.register_feature('register',
                self._handle_register_feature,
                restart=False,
                order=self.config.get('order', 50))

        register_stanza_plugin(Register, self.xmpp['xep_0004'].stanza.Form)
        register_stanza_plugin(Register, self.xmpp['xep_0066'].stanza.OOB)

    def _handle_register_feature(self, features):
        if 'mechanisms' in self.xmpp.features:
            # We have already logged in with an account
            return False

        if self.create_account:
            form = self.get_registration()
            self.xmpp.event('register', form, direct=True)
            return True
        return False

    def get_registration(self, jid=None, ifrom=None, block=True,
                         timeout=None, callback=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'get'
        iq['to'] = jid
        iq['from'] = ifrom
        iq.enable('register')
        return iq.send(block=block, timeout=timeout, callback=callback, now=True)

    def cancel_registration(self, jid=None, ifrom=None, block=True,
                            timeout=None, callback=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['to'] = jid
        iq['from'] = ifrom
        iq['register']['remove'] = True
        return iq.send(block=block, timeout=timeout, callback=callback)

    def change_password(self, password, jid=None, ifrom=None, block=True,
                        timeout=None, callback=None):
        iq= self.xmpp.Iq()
        iq['type'] = 'set'
        iq['to'] = jid
        iq['from'] = ifrom
        if self.xmpp.is_component:
            ifrom = JID(ifrom)
            iq['register']['username'] = ifrom.user
        else:
            iq['register']['username'] = self.xmpp.boundjid.user
        iq['register']['password'] = password
        return iq.send(block=block, timeout=timeout, callback=callback)


register_plugin(XEP_0077)
