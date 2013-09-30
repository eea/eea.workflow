""" Archival views
"""

from DateTime import DateTime
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from eea.workflow.interfaces import IObjectArchivator


class Reasons(BrowserView):
    """ Returns a dict of reasons
    """

    def __call__(self):
        rv = NamedVocabulary('eea.workflow.reasons')    #TODO: rename to eea.workflow.archive_reasons
        reasons = rv.getVocabularyDict(self.context)
        return reasons


class ArchiveContent(BrowserView):
    """ Archive the context object
    """

    def __call__(self, **kwargs):
        # TODO: validate form using zope.schema
        form = self.request.form
        values = {'initiator':      form.get('workflow_archive_initiator'),
                  'custom_message': form.get('workflow_other_reason', '').strip(),
                  'reason':         form.get('workflow_reasons_radio', 'other')
                  }
        storage = IObjectArchivator(self.context)
        storage.archive(context=self.context, **values)
        return "OK"


class ArchiveStatus(BrowserView):
    """ Show the same info as the archive status viewlet
    """

    @property
    def info(self):
        return IObjectArchivator(self.context)

