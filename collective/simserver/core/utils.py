# -*- coding: utf-8 -*-
import re
import Pyro4
from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from collective.simserver.core.interfaces import ISimserverSettingsSchema
PAT_ALPHABETIC = re.compile('(((?![\d])\w)+)', re.UNICODE)

def get_session_server():
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISimserverSettingsSchema)
    name = settings.simserver_name
    sock = settings.pyro_ns_socket
    host = settings.pyro_ns_host
    port = settings.pyro_ns_port
    if sock:
        try:
            service = Pyro4.Proxy(Pyro4.locateNS(sock).lookup(name))
            return service
        except:
            pass
    if host:
        try:
            service = Pyro4.Proxy(Pyro4.locateNS(host, port).lookup(name))
            return service
        except:
            pass
    service = Pyro4.Proxy(Pyro4.locateNS().lookup(name))
    return service


def tokenize(text, lowercase=False, deacc=False, errors="strict", to_lower=False, lower=False):
    """
    Iteratively yield tokens as unicode strings, optionally also lowercasing them
    and removing accent marks.

    Input text may be either unicode or utf8-encoded byte string.

    The tokens on output are maximal contiguous sequences of alphabetic
    characters (no digits!).

    >>> list(tokenize('Nic nemůže letět rychlostí vyšší, než 300 tisíc kilometrů za sekundu!', deacc = True))
    [u'Nic', u'nemuze', u'letet', u'rychlosti', u'vyssi', u'nez', u'tisic', u'kilometru', u'za', u'sekundu']
    """
    lowercase = lowercase or to_lower or lower
    if not isinstance(text, unicode):
        text = unicode(text, encoding='utf8', errors=errors)
    if lowercase:
        text = text.lower()
    if deacc:
        text = deaccent(text)
    for match in PAT_ALPHABETIC.finditer(text):
        yield match.group()

def simple_preprocess(doc):
    """
    Convert a document into a list of tokens.

    This lowercases, tokenizes, stems, normalizes etc. -- the output are final,
    utf8 encoded strings that won't be processed any further.
    """
    tokens = [token.encode('utf8') for token in tokenize(doc, lower=True, errors='ignore')
            if 2 <= len(token) <= 15 and not token.startswith('_')]
    return tokens
