# -*- coding: utf-8 -*-
from z3c.form import button
from plone.app.registry.browser import controlpanel
from collective.simserver.core import simserverMessageFactory as _
from collective.simserver.core.interfaces import ISimserverSettingsSchema
from zope.app.component.hooks import getSite
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


class SimserverSettings(controlpanel.RegistryEditForm):
    #form_fields = form.FormFields(ITagHelperSettingsSchema)
    schema = ISimserverSettingsSchema
    label = _(u'Simserver Settings')
    description = _(u'How to connect to your simserver')

    def updateFields(self):
        super(SimserverSettings, self).updateFields()

    def updateWidgets(self):
        super(SimserverSettings, self).updateWidgets()

    @button.buttonAndHandler(_('Train and Index'), name='train')
    def actionTrain(self, action):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimserverSettingsSchema)
        settinguid= settings.corpus_collection
        site = getSite()
        topic = site.reference_catalog.lookupObject(settinguid)
        next_url = topic.absolute_url() + '/@@simserver-corpus.html'
        self.request.response.redirect(next_url)

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))


class SimserverSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SimserverSettings
