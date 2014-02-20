# -*- coding: utf-8 -*-
import logging
from zope import interface, schema
from zope.formlib import form
from zope.component import getUtility
from zope.app.component.hooks import getSite

from five.formlib import formbase

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


from plone.registry.interfaces import IRegistry

from collective.simserver.core import simserverMessageFactory as _
from collective.simserver.core.interfaces import ISimserverSettingsSchema
from collective.simserver.core import utils


try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger('collective.simserver.core')

# Ignore articles shorter than ARTICLE_MIN_CHARS characters.
ARTICLE_MIN_CHARS = 700

class NeitherExportNorDirect(schema.ValidationError):
     u"""Please specify if you want to
        export and/or process directly"""


class IExportForm(interface.Interface):
    ''' Form fields for the export form '''
    export_to_fs = schema.Bool(
        title=_(u'Export to filesystem'),
        description=_(u"""Export all the documents to the filesystem
                    for later processing"""),
        required=False,
        readonly=False,
        default=False,
        )

    process_directly = schema.Bool(
        title=_(u'Process directly'),
        description=_(u"""send the documents directly to the simserver"""),
        required=False,
        readonly=False,
        default=False,
        )


    @interface.invariant
    def neither_export_nor_direct(export):
        if not export.export_to_fs and not export.process_directly:
            raise NeitherExportNorDirect, (_(u"""Please specify if you
                want to export and/or process directly"""),
                'export_to_fs', 'process_directly')


class IIndexForm(IExportForm):
    ''' Form fields for the index form'''

    upload_chunked = schema.Int(
        title = _(u'Chunksize'),
        description = _(u"""send n documents at a time (saves RAM but slower)
                    only applicable for online indexing """),
        required = False,
        readonly = False,
        default = 200,
        min = 0,
        max = 5000,
        )

    new_only = schema.Bool(
        title=_(u'Only new documents'),
        description=_(u"""send only documents not yet indexed to the simserver"""),
        required=False,
        readonly=False,
        default=False,
        )

class IQueryForm(interface.Interface):
    '''Form fields for the query form'''

    text = schema.Text(
        title=_(u'Input text'),
        description=_(u"""Find documents similar to this text"""),
        required=True,
        readonly=False,
    )

class ExportForm(formbase.PageForm):
    form_fields = form.FormFields(IExportForm)
    buffer = []

    def __init__( self, context, request ):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISimserverSettingsSchema)
        self.settinguid= self.settings.corpus_collection
        if self.settings.export_path .endswith('/'):
            self.path = self.settings.export_path
        else:
            self.path = self.settings.export_path + '/'
        super( ExportForm, self).__init__( context, request )
        try:
            self.service = utils.SimService()
            response = self.service.status()
            if response['status'] == 'OK':
                IStatusMessage(self.request).addStatusMessage(
                        response['response'], type='info')
            else:
                IStatusMessage(self.request).addStatusMessage(
                        response['response'], type='error')
        except:
            self.service = None
            status = _(u'Error connecting to simserver')
            IStatusMessage(self.request).addStatusMessage(status, type='error')


    def buffer_documents(self, brains, path, online=False,
            offline=True, min_chars=ARTICLE_MIN_CHARS):
        i=0
        for brain in brains:
            ob = brain.getObject()
            id = ob.getId()
            text = ob.SearchableText()
            text = text.strip()
            text = text.decode('utf-8', 'ignore')
            text = text.encode('utf-8')
            uid = ob.UID()
            if len(text) < min_chars:
                continue
            else:
                if online:
                    tmp = ''
                    try:
                        # try to convert it to json and only buffer it
                        # when it could be successfully dumped
                        tmp = json.dumps({'id': uid, 'text': text})
                        self.buffer.append({'id': uid, 'text': text})
                        logger.info('bufferd %s' % uid)
                    except:
                        logger.error('cannot dump %s as json' % uid)
                if offline:
                    fname = path + uid
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

    def update(self):
        super(ExportForm, self).update()
        for widget in self.widgets:
            name = widget.context.getName()
            for error in self.errors:
                if name in error.args:
                    widget._error = error

class TrainForm(ExportForm):
    label = _(u'Train on a corpus')
    description = _(u'''To be able to extract information from the
    simserver you need to build a corpus. The service indexes
    documents in a semantic representation so we must teach the
    service how to convert between plain text and semantics first ''')


    @form.action('train')
    def actionTrain(self, action, data):
        if self.service is None:
            status = _(u'Error connecting to simserver')
            IStatusMessage(self.request).addStatusMessage(status, type='error')
            return
        contextuid = self.context.UID()
        path = self.path + 'corpus/'
        site = getSite()
        online = data['process_directly']
        offline = data['export_to_fs']
        if contextuid != self.settinguid:
            topic = site.reference_catalog.lookupObject(self.settinguid)
            next_url = topic.absolute_url() + '/@@' + self.__name__
            status = _(u"""you can only train documents on the topic
                            you specified in the controlpanel""")
            IStatusMessage(self.request).addStatusMessage(status,
                                                type='error')
            status = _('you have been redirected to this topic')
            IStatusMessage(self.request).addStatusMessage(status,
                                                    type='info')
            self.request.response.redirect(next_url)
        else:
            try:
                i = self.buffer_documents(self.context.queryCatalog(),
                                                path, online, offline)
                if online:
                    logger.info('exported %i documents. Start training' % i)
                    respone = self.service.train(self.buffer)
                    if response['status'] == 'OK':
                        logger.info('training complete')
                        status = _('changes commited, index trained')
                        IStatusMessage(self.request).addStatusMessage(
                                                status, type='info')
                    else:
                        IStatusMessage(self.request).addStatusMessage(
                                    response['response'], type='error')
                else:
                    logger.info('exported %i documents.' % i)
                    status = _('export successfull')
                    IStatusMessage(self.request).addStatusMessage(
                                            status, type='info')
                self.request.response.redirect(self.next_url)
            except:
                status = _(u'error building corpus, index unchanged')
                logger.warn(status)
                IStatusMessage(self.request).addStatusMessage(status,
                                                type='error')

    @form.action('Cancel')
    def actionCancel(self, action, data):
        status = _(u'canceled')
        IStatusMessage(self.request).addStatusMessage(status, type='info')
        self.request.response.redirect(self.next_url)



class IndexForm(ExportForm):
    form_fields = form.FormFields(IIndexForm)
    label = _(u'Index documents')
    description = _(u'''To be able to extract information from the
    simserver you need to index your documents. When you pass documents
    that have the same uid as some already indexed document, the indexed
    document is overwritten by the new input. You don’t have to index
    all documents first to start querying,
    indexing can be incremental. ''')

    @form.action('index')
    def actionIndex(self, action, data):
        if self.service is None:
            status = _(u'Error connecting to simserver')
            IStatusMessage(self.request).addStatusMessage(status, type='error')
            return
        path = self.path + 'index/'
        contextuid = self.context.UID()
        online = data['process_directly']
        offline = data['export_to_fs']
        chunksize = data['upload_chunked']
        results = self.context.queryCatalog()
        if data['new_only']:
            qresults = []
            idx_response = self.service.indexed_documents()
            if idx_response['status'] == 'OK':
                qresults = [r for r in results
                            if r.UID not in idx_response['response']]
        else:
           qresults = results
        logger.info('start indexing, %i documents to index' % len(qresults))
        if chunksize and online:
            j = 0
            k = 0
            while j*chunksize < len(qresults):
                i = self.buffer_documents(
                                qresults[j*chunksize:(j+1)*chunksize],
                                path, online, offline, 300)
                j += 1
                response = self.service.index(self.buffer)
                if response['status'] == 'OK':
                    logger.info('indexed %i documents' % response['response'])
                    k += response['response']
                else:
                    logger.info(response['response'])
                self.buffer =[]
            logger.info('indexing complete, indexed %i documents' % k)
            status = _(u"Documents indexed")
            IStatusMessage(self.request).addStatusMessage(status,
                                                type='info')

        elif online:
            i = self.buffer_documents(qresults, path, online, offline, 300)
            response = self.service.index(self.buffer)
            if response['status'] == 'OK':
                logger.info('indexing complete, indexed %i documents' %
                                            response['response'])
                status = _(u'Documents indexed')
                IStatusMessage(self.request).addStatusMessage(status,
                                                    type='info')
            else:
                logger.info(response['response'])
                IStatusMessage(self.request).addStatusMessage(
                                    response['response'], type='error')
        else:
            i = self.buffer_documents(qresults, path, False, True, 300)
            status = _('Documents exported')
            IStatusMessage(self.request).addStatusMessage(status,
                                                type='info')
            logger.info('exported %i documents' % i)
        self.request.response.redirect(self.next_url)


    @form.action('Remove from index')
    def actionDelete(self, action, data):
        if self.service is None:
            status = _(u'Error connecting to simserver')
            IStatusMessage(self.request).addStatusMessage(status, type='error')
            return
        results = self.context.queryCatalog()
        uids = [r.UID for r in results]
        response = self.service.delete(uids)
        if response['status'] == 'OK':
            status = _(u'Documents removed from index')
            IStatusMessage(self.request).addStatusMessage(status,
                                                type='info')
        else:
            status = _(u'Error while removing documents from index')
            IStatusMessage(self.request).addStatusMessage(status,
                                                type='error')
        self.request.response.redirect(self.next_url)

    @form.action('Cancel')
    def actionCancel(self, action, data):
        status = _(u'canceled')
        IStatusMessage(self.request).addStatusMessage(status, type='info')
        self.request.response.redirect(self.next_url)


class QueryForm(formbase.PageForm):
    ''' Display a form in which a user can input text and documents
    similar to this text are returned'''
    form_fields = form.FormFields(IQueryForm)
    template = ViewPageTemplateFile('query.pt')

    def __init__( self, context, request ):
        super(QueryForm, self).__init__( context, request )
        self.results = []
        try:
            self.service = utils.SimService()
            response = self.service.status()
            if response['status'] == 'OK':
                IStatusMessage(self.request).addStatusMessage(
                        response['response'], type='info')
            else:
                IStatusMessage(self.request).addStatusMessage(
                        response['response'], type='error')
        except:
            self.service = None
            status = _(u'Error connecting to simserver')
            IStatusMessage(self.request).addStatusMessage(status, type='error')

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @form.action('Search')
    def actionQuery(self, action, data):
        if self.service is None:
            status = _(u'Error connecting to simserver')
            IStatusMessage(self.request).addStatusMessage(status, type='error')
            return
        response = self.service.query(text=data)
        items = {}
        similarities = {}
        if response['status'] == 'OK':
            uids = [r[0] for r in response['response']]
            for item in response['response']:
                similarities[item[0]] = item[1]
            brains = self.portal_catalog(UID = similarities.keys())
            for brain in brains:
                similarity = similarities.get(brain.UID, 0)
                items[brain.UID] = {'url': brain.getURL(),
                        'uid': brain.UID,
                        'title': brain.Title,
                        'desc': brain.Description,
                        'state': brain.review_state,
                        'icon': brain.getIcon,
                        'similarity': similarity,
                        'tags': brain.Subject,
                        }
        if items:
            for item in response['response']:
                if item[0] in items:
                    self.results.append(items[item[0]])
