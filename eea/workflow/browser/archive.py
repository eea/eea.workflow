""" Archival views
"""
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from zope.component import getMultiAdapter
from plone.protect import PostOnly
from eea.workflow.archive import archive_object, archive_previous_versions, \
    archive_children, archive_translations, \
    unarchive_object, unarchive_children, unarchive_translations
from eea.workflow.interfaces import IObjectArchivator


class Reasons(BrowserView):
    """ Returns a dict of reasons
    """

    def __call__(self):
        rv = NamedVocabulary('eea.workflow.reasons')
        reasons = rv.getVocabularyDict(self.context)
        return reasons


class ArchiveContent(BrowserView):
    """ Archive the context object
    """

    def __call__(self, **kwargs):
        PostOnly(self.request)
        form = self.request.form
        recurse = form.has_key('workflow_archive_recurse')
        prev_versions = form.has_key('workflow_archive_previous_versions')
        translations = form.has_key('workflow_archive_translations')
        val = {'initiator': form.get('workflow_archive_initiator', ''),
               'custom_message': form.get('workflow_other_reason', '').strip(),
               'reason': form.get('workflow_reasons_radio', 'other'),
        }

        context = self.context
        ploneview = getMultiAdapter((context, self.request), name='plone')
        if ploneview.isDefaultPageInFolder():
            context = self.context.getParentNode()

        archive_object(context, **val)
        if recurse:
            archive_children(context, **val)
        if prev_versions:
            archive_previous_versions(context, also_children=recurse, **val)
        if translations:
            archive_translations(context, also_children=recurse,
                also_versions=prev_versions, **val)

        return "OK"


class UnArchiveContent(BrowserView):
    """ UnArchive the context object
    """

    def __call__(self, **kwargs):
        PostOnly(self.request)
        form = self.request.form
        recurse = form.has_key('workflow_unarchive_recurse')
        translations = form.has_key('workflow_unarchive_translations')

        context = self.context
        ploneview = getMultiAdapter((context, self.request), name='plone')
        if ploneview.isDefaultPageInFolder():
            context = self.context.getParentNode()

        unarchive_object(context)
        msg = "Object has been unarchived"
        if recurse:
            unarchive_children(context)
            msg = "Object and contents have been unarchived"
        if translations:
            unarchive_translations(context, also_children=recurse)
            if recurse:
                msg = "Object, contents and translations have been unarchived"
            else:
                msg = "Object and translations have been unarchived"

        IStatusMessage(context.REQUEST).add(msg, 'info')

        return self.request.response.redirect(context.absolute_url())


class ArchiveStatus(BrowserView):
    """ Show the same info as the archive status viewlet
    """

    @property
    def info(self):
        """ Info used in view
        """
        info = IObjectArchivator(self.context)

        rv = NamedVocabulary('eea.workflow.reasons')
        vocab = rv.getVocabularyDict(self.context)

        archive_info = dict(initiator=info.initiator,
                            archive_date=info.archive_date,
                            reason=vocab.get(info.reason, "Other"),
                            custom_message=info.custom_message)

        return archive_info
