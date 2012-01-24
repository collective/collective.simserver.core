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
        required=True,
        vocabulary ='simserver.core.topics',
        )

    simserver_name = schema.TextLine(
        title=_(u'Simserver Name'),
        description=_(u'Name of the simserver to connect to'),
        required=False,
        readonly=False,
        default=u'collective.simserver',
        )


    restsims_url = schema.TextLine(
        title=_(u'Restful Simserver URL'),
        description=_(u'''URL of the server (e.g. http://localhost:6543/)'''),
        required=True,
        readonly=False,
        default=u'http://localhost:6543',
        )

    min_score = schema.Float(
        title = _("Min score"),
        description = _("Minimal score"),
        required = True,
        readonly = False,
        default = 0.4,
        min = 0.0,
        max = 1.0,
        )

    max_results = schema.Int(
        title= _(u'Max Results'),
        description = _(u'Maximum number of results returned'),
        required = True,
        readonly = False,
        default = 100,
        min = 1,
        max = 200,
        )
