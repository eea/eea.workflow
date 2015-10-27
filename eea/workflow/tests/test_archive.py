""" Test archive functionality
"""
from eea.versions.versions import create_version
from eea.workflow.archive import archive_object, archive_children, \
    archive_obj_and_children, archive_previous_versions, \
    archive_translations, unarchive_object, unarchive_children, \
    unarchive_translations
from eea.workflow.tests.base import TestCase
from eea.workflow.interfaces import IObjectArchived

class TestArchive(TestCase):
    """ TestArchive TestCase class
    """

    def afterSetUp(self):
        """ After Setup
        """
        self.setRoles(('Manager', ))
        portal = self.portal
        fid = portal.invokeFactory("Folder", 'f1')
        self.folder = portal[fid]
        docid = self.folder.invokeFactory("Document", 'd1')
        self.doc = self.folder[docid]

    def test_archive_object(self):
        """ Test the archival of the object
        """
        archive_object(self.folder)
        assert IObjectArchived.providedBy(self.folder)

    def test_archive_obj_and_children(self):
        """ Test the archival of the object and children
        """
        archive_obj_and_children(self.folder)
        assert IObjectArchived.providedBy(self.folder)
        assert IObjectArchived.providedBy(self.doc)

    def test_archive_previous_versions(self):
        """ Test the archival of the previous versions
            for the given object
        """
        version = create_version(self.folder)
        archive_previous_versions(version)
        assert not IObjectArchived.providedBy(version)
        assert IObjectArchived.providedBy(self.folder)

    def test_archive_previous_versions_without_children(self):
        """ Test the archival of the previous versions
            for the given object even when calling the method
            that should archive also the children
        """
        fid = self.portal.invokeFactory("Folder", 'f2')
        self.folder = self.portal[fid]
        version = create_version(self.folder)
        archive_previous_versions(version, also_children=True)
        assert not IObjectArchived.providedBy(version)
        assert IObjectArchived.providedBy(self.folder)

    def test_archive_previous_versions_with_children(self):
        """ Test the archival of the previous versions
            for the given object and their children
        """
        version = create_version(self.folder)
        archive_previous_versions(version, also_children=True)
        assert not IObjectArchived.providedBy(version)
        assert IObjectArchived.providedBy(self.folder)
        assert IObjectArchived.providedBy(self.doc)

    def test_archive_previous_versions_with_children_return(self):
        """ Test the return value for archival of the previous versions
            for the given object and their children
        """
        version = create_version(self.folder)
        objects = archive_previous_versions(version, also_children=True)
        expected_output = [self.folder, self.doc]
        assert objects == expected_output

class TestUnarchive(TestCase):
    """ TestUnarchive TestCase class
    """

    def afterSetUp(self):
        """ After Setup
        """
        self.setRoles(('Manager', ))
        portal = self.portal

        #setup content and translations
        fid = portal.invokeFactory("Folder", 'f1')
        self.folder = portal[fid]
        trans = self.folder.addTranslation('ro')
        self.folder.addTranslationReference(trans)
        self.folder_ro = self.folder.getTranslation('ro')
        assert self.folder_ro.isTranslation() == True
        assert self.folder_ro.getLanguage() == 'ro'
        docid = self.folder.invokeFactory("Document", 'd1')
        self.doc = self.folder[docid]

        trans = self.doc.addTranslation('ro')
        self.doc.addTranslationReference(trans)
        self.doc_ro = self.doc.getTranslation('ro')
        assert self.doc_ro.isTranslation() == True
        assert self.doc_ro.getLanguage() == 'ro'
        assert self.doc_ro.getTranslation() == self.doc

        #print 'self.doc', self.doc, self.doc.getParentNode()
        #print 'self.doc_ro', self.doc_ro, self.doc_ro.getParentNode()

        #archive content
        archive_object(self.folder)
        assert IObjectArchived.providedBy(self.folder)
        archive_children(self.folder)
        assert IObjectArchived.providedBy(self.doc)
        archive_translations(self.folder, also_children=True)
        assert IObjectArchived.providedBy(self.folder_ro)
        assert IObjectArchived.providedBy(self.doc_ro)

    def test_unarchive_object(self):
        """ Test the unarchival of the object
        """
        unarchive_object(self.folder)
        assert not IObjectArchived.providedBy(self.folder)

    def test_unarchive_obj_and_children(self):
        """ Test the unarchival of the object and children
        """
        unarchive_object(self.folder)
        objects = unarchive_children(self.folder)
        expected_output = [self.doc]
        assert not IObjectArchived.providedBy(self.folder)
        assert not IObjectArchived.providedBy(self.doc)
        assert objects == expected_output

    def test_unarchive_obj_and_translations(self):
        """ Test the unarchival of the object and translations
        """
        unarchive_object(self.folder)
        objects = unarchive_translations(self.folder)
        expected_output = [self.folder_ro]
        assert not IObjectArchived.providedBy(self.folder)
        assert not IObjectArchived.providedBy(self.folder_ro)
        assert objects == expected_output

    def test_unarchive_obj_and_children_translations(self):
        """ Test the unarchival of the object and translations
        """
        unarchive_object(self.folder)
        objects = unarchive_children(self.folder)
        objects.extend(unarchive_translations(self.folder, also_children=True))
        expected_output = [self.doc, self.folder_ro, self.doc_ro]
        assert not IObjectArchived.providedBy(self.folder)
        assert not IObjectArchived.providedBy(self.folder_ro)
        assert not IObjectArchived.providedBy(self.doc)
        assert not IObjectArchived.providedBy(self.doc_ro)
        assert objects == expected_output

def test_suite():
    """ Test Suite
    """
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestArchive))
    suite.addTest(makeSuite(TestUnarchive))
    return suite
