# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from collective.simserver.core import simserverMessageFactory as _
from collective.simserver.core.interfaces import ISimserverSettingsSchema

class SimserverSettings(controlpanel.RegistryEditForm):
    #form_fields = form.FormFields(ITagHelperSettingsSchema)
    schema = ISimserverSettingsSchema
    label = _(u'Simserver Settings')
    description = _(u'How to connect to your simserver')

    def updateFields(self):
        super(SimserverSettings, self).updateFields()

    def updateWidgets(self):
        super(SimserverSettings, self).updateWidgets()


class SimserverSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SimserverSettings
