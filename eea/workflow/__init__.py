""" Init
"""
from zope.i18nmessageid import MessageFactory

from Products.CMFCore import DirectoryView
from eea.workflow import patches  #install patches for Products.CMFCore

PortletReadinessMessageFactory = MessageFactory('eea.workflow')


__all__ = [
        patches.__name__,
        DirectoryView.__name__,
]
