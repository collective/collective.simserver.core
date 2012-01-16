# -*- coding: utf-8 -*-
from zope import interface, schema

from plone.theme.interfaces import IDefaultPloneLayer

from collective.simserver.core import simserverMessageFactory as _


class ISimserverLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """


class ISimserverSettingsSchema(interface.Interface):
    """ Plone controllpanel settings for Simserver """

    export_path = schema.TextLine(
        title=_(u'Corpus Export Path'),
        description=_(u'Path to export the corpus to'),
        required=False,
        readonly=False,
        default=None,
        )

    corpus_collection = schema.Choice(
        title=_(u"Corpus collection"),
        description=_(u"Find the collection which provides the items to be exported as the corpus"),
        required=False,
        vocabulary ='simserver.core.topics',
        )

    simserver_name = schema.TextLine(
        title=_(u'Simserver Name'),
        description=_(u'Name of the simserver to connect to'),
        required=True,
        readonly=False,
        default=u'collective.simserver',
        )

    pyro_ns_socket = schema.TextLine(
        title=_(u'Pyro4 Nameserver socket'),
        description=_(u'''Unix domain socket the Pyro Nameserver runs on (e.g. ./u:/tmp/pyrons.pid).
                    You have either to provide the socket or host and port.
                    If socket and host and port are given we will first try to connect
                    via the socket and if that fails connect to the host:port'''),
        required=False,
        readonly=False,
        default=u'./u:/tmp/pyrons.pid',
        )

    pyro_ns_host = schema.TextLine(
        title=_(u'Pyro4 Nameserver host'),
        description=_(u'''Host the Pyro Nameserver runs on (e.g. localhost)
                    You have either to provide the socket or host and port.'''),
        required=False,
        readonly=False,
        default=u'localhost',
        )

    pyro_ns_port = schema.Int(
        title=_(u'Pyro4 Nameserver port'),
        description=_(u'''Port the Pyro Nameserver runs on (e.g. 9900)
                    You have either to provide the socket or host and port.'''),
        required=False,
        readonly=False,
        default=9090,
        )
