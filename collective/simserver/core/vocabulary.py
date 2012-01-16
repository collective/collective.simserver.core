# -*- coding: utf-8 -*-
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from collective.simserver.core.interfaces import ISimserverSettingsSchema

def topic_vocab_factory(context):
    """get all potential topics for corpuses"""
    try:
        registry = getUtility(IRegistry)
        site = registry.getParentNode()
        catalog = getToolByName(site, 'portal_catalog')
        query = {'portal_type': 'Topic', 'sort_on': 'sortable_title'}
        brains = catalog(**query)
        ppl = len('/'.join(site.getPhysicalPath()))
        items=[(brain.Title[:15] +' - ' + brain.getPath()[ppl:], brain.UID)
            for brain in brains]
        return SimpleVocabulary.fromItems(items)
    except:
        return SimpleVocabulary.fromItems([('Title', 'UID'),])
