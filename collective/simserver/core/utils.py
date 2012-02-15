# -*- coding: utf-8 -*-
import urllib, urllib2
import logging
try:
    import simplejson as json
    from simplejson.decoder import JSONDecodeError
except ImportError:
    import json
    JSONDecodeError = ValueError

from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from collective.simserver.core.interfaces import ISimserverSettingsSchema

logger = logging.getLogger('collective.simserver.core')

class SimService(object):


    def __init__(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimserverSettingsSchema)
        self.url = settings.restsims_url
        self.min_score = settings.min_score
        self.max_results = settings.max_results

    def rest_post(self, content):
        content['format'] = 'json'
        content['submit'] = 'submit'
        params = urllib.urlencode(content)
        response = urllib2.urlopen(self.url, data=params)
        data = response.read()
        try:
            return json.loads(data)
        except (JSONDecodeError, ValueError):
            return {'status': 'UNKNOWN', 'response': 'JSONDecodeError'}

    def status(self):
        """ Return the simserver status """
        content = {'action':'status'}
        return self.rest_post(content)

    def train(self, corpus):
        """ Corpus is a list of dictionaries. Each dictionary must be
            either: {'id': UID, 'text': Text}
            or: {'id': UID, 'tokens': ['List', 'of', 'tokens']} """
        content = {'action': 'train',
                    'text': json.dumps(corpus)}
        return self.rest_post(content)

    def index(self, corpus):
        """ Corpus is a list of dictionaries. Each dictionary must be
            either: {'id': UID, 'text': Text}
            or: {'id': UID, 'tokens': ['List', 'of', 'tokens']} """
        content = {'action': 'index',
                    'text': json.dumps(corpus)}
        return self.rest_post(content)

    def delete(self, documents):
        """ documents is a list of UIDs to be deleted """
        content = {'action': 'delete',
                    'text': json.dumps(documents)}
        return self.rest_post(content)

    def optimize(self):
        """ Optimize the index """
        content = {'action': 'optimize'}
        return self.rest_post(content)

    def indexed_documents(self):
        """ Return a list of indexed documents"""
        content = {'action': 'documents'}
        return self.rest_post(content)

    def is_indexed(self, document):
        """ Return if document is in index """
        content = {'action': 'is_indexed',
                    'text': document}
        return self.rest_post(content)

    def query(self, documents=None, text=None, min_score=None, max_results=None):
        """ either query for a list of documents [UID,]
        or a plain text that will be compared to the indexed documents
        @returns either a list of documents if text
                or a dictionary {UID : [similar] """
        content = {'action':'query'}
        if min_score:
            content['min_score'] = min_score
        else:
            content['min_score'] = self.min_score
        if max_results:
            content['max_results'] = max_results
        else:
            content['max_results'] = self.max_results

        if documents:
            content['text'] = json.dumps(documents)
        elif text:
            content['text'] = text
        else:
            return {'status': 'NODATA', 'response':
                'Either text or documents must be specified'}
        return self.rest_post(content)


def index_and_relate(context, event):
    if hasattr(context, 'SearchableText'):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimserverSettingsSchema)
        if settings.index_created:
            if context.portal_type in settings.content_types:
                id = context.getId()
                text = context.SearchableText()
                text = text.strip()
                text = text.lstrip(id).lstrip()
                text = text.decode('utf-8', 'ignore')
                text = text.encode('utf-8')
                uid = context.UID()
                service = SimService()
                response = service.index([{'id': uid, 'text': text}])
                if response['status'] == 'OK':
                    logger.info('indexed %i documents' % response['response'])
                else:
                    return
            else:
                return
        else:
            return
        if settings.relate_similar:
            response = service.query([uid],
                max_results = settings.relate_similar +1)
            if response['status'] == 'OK':
                simserveritems = response['response']
                if uid in simserveritems:
                    suids =[s[0] for s in simserveritems[uid]
                                if uid != s[0]]
                else:
                    return
                portal_catalog = getToolByName(context, 'portal_catalog')
                brains = portal_catalog(UID = suids)
                uids_in_cat = [brain.UID for brain in brains]
                uids = [uid for uid in suids if uid in uids_in_cat]
                context.setRelatedItems(uids)
                logger.info('related %i documents' % len(uids))

