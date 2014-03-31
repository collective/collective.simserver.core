# -*- coding: utf-8 -*-
from zope import interface, schema

from plone.theme.interfaces import IDefaultPloneLayer

from collective.simserver.core import simserverMessageFactory as _


class ISimserverLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """


class ISimserverSettingsSchema(interface.Interface):
    """ Plone Control Panel settings for Simserver """

    export_path = schema.TextLine(
        title=_(u'Corpus Export Path'),
        description=_(u"""Path to export the corpus to 
            (note that this should be unique per Zope instance, 
            as the corpus is keyed on object UID)"""),
        required=False,
        readonly=False,
        default=None,
        )

    corpus_collection = schema.Choice(
        title=_(u"Corpus collection"),
        description=_(u"""Find the collection which provides the items
                            to be exported as the corpus"""),
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

    index_created = schema.Bool(
        title=_(u'Index automatically'),
        description=_(u"""Index content upon creation
                        (only below contentypes)."""),
        required=False,
        readonly=False,
        default=True,
        )


    content_types = schema.List(
        title = _(u'Content types'),
        description = _(u"""Content types to be indexed upon creation
                        (only applicable if
                        'Index automatically' is enabled)"""),
        required = False,
        default = [u"File", u"Document", u'News Item', u'Event'],
        value_type = schema.Choice(title=_(u"Content types"),
                    source="plone.app.vocabularies.ReallyUserFriendlyTypes"))

    relate_similar = schema.Int(
        title=_(u'Relate to similar items'),
        description=_(u"""Automatically assign the n most similar items as
                        related content (0 = disable, only applicable if
                        'Index automatically' is enabled)"""),
        required=False,
        readonly=False,
        min = 0,
        max = 20,
        default=7,
        )
