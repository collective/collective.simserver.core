# -*- coding: utf-8 -*-
import logging
from zope import interface, schema
from zope.formlib import form
from zope.component import getUtility
from zope.app.component.hooks import getSite

from five.formlib import formbase

from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry

from collective.simserver.core import simserverMessageFactory as _
from collective.simserver.core.interfaces import ISimserverSettingsSchema
from collective.simserver.core import utils



logger = logging.getLogger('collective.simserver.core')

# Ignore articles shorter than ARTICLE_MIN_CHARS characters (after preprocessing).
ARTICLE_MIN_CHARS = 700


class ExportCorpus(formbase.PageForm):

    form_fields =[]

    def buffer_documents(self, service, brains, path):
        i=0
        for brain in brains:
            ob = brain.getObject()
            id = ob.getId()
            text = ob.SearchableText()
            text = text.strip()
            text = text.lstrip(id).lstrip()
            text.decode('utf-8', 'ignore')
            uid = ob.UID()
            if len(text) < ARTICLE_MIN_CHARS:
                continue
            else:
                service.buffer([{'id': uid, 'tokens': utils.simple_preprocess(text)}])
                fname = path + uid +'.txt'
                f = open(fname, 'w')
                f.write(text)
                f.flush()
                f.close()
                i += 1
                logger.info('exported %s' % fname)
        return i

    @property
    def next_url(self):
        url = self.context.absolute_url()
        return url

    @form.action('train')
    def actionTrain(self, action, data):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimserverSettingsSchema)
        settinguid= settings.corpus_collection
        path = settings.export_path + '/corpus/'
        contextuid = self.context.UID()
        site = getSite()
        if contextuid != settinguid:
            topic = site.reference_catalog.lookupObject(settinguid)
            next_url = topic.absolute_url() + '/@@' + self.__name__
            self.request.response.redirect(next_url)
        else:
            service = utils.get_session_server()
            service.set_autosession(False)
            service.open_session()
            i = self.buffer_documents(service, self.context.queryCatalog(), path)
            logger.info('exported %i documents. Start training' % i)
            service.train(method='lsi')
            logger.info('training complete commit changes')
            service.commit()
            logger.info('changes commited, index trained on %i documents' % i)
            self.request.response.redirect(self.next_url)


    @form.action('index')
    def actionIndex(self, action, data):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimserverSettingsSchema)
        settinguid= settings.corpus_collection
        path = settings.export_path + '/index/'
        contextuid = self.context.UID()
        site = getSite()
        if contextuid != settinguid:
            topic = site.reference_catalog.lookupObject(settinguid)
            next_url = topic.absolute_url() + '/@@' + self.__name__
            self.request.response.redirect(next_url)
        else:
            service = utils.get_session_server()
            service.set_autosession(False)
            service.open_session()
            try:
                i = self.buffer_documents(service, self.context.queryCatalog(),path)
                logger.info('exported %i documents. Start indexing' % i)
                service.index()
                logger.info('indexing complete commit changes')
                service.commit()
                logger.info('changes commited, indexed %i documents' % i)
            except:
                logger.warn('error indexing documents, index unchanged')
            self.request.response.redirect(self.next_url)


    @form.action('Cancel')
    def actionCancel(self, action, data):
        self.request.response.redirect(self.next_url)
