""" Async
"""
from urlparse import urlsplit
from Products.Five import BrowserView
from Products.statusmessages import STATUSMESSAGEKEY
from Products.statusmessages.adapter import _decodeCookieValue
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class WorkflowMenu(BrowserView):
    """Returns the workflow menu as an independent page.

    This allows reloading it through AJAX
    """

    implements(IViewView)   #needed for plone viewlet registrations
    messages = None

    def cancel_redirect(self):
        """ Cancel
        """
        if self.request.response.getStatus() in (302, 303):
            # Try to not redirect if requested
            self.request.response.setStatus(200)

    def get_portal_messages(self):
        """ Portal message
        """
        statusmessages = []
        if hasattr(self.request.RESPONSE, 'cookies'):
            cookie = self.request.RESPONSE.cookies.get(STATUSMESSAGEKEY)
            if cookie:
                encodedstatusmessages = cookie['value']
                statusmessages = _decodeCookieValue(encodedstatusmessages)

        self.request.RESPONSE.expireCookie(STATUSMESSAGEKEY, path='/')
        return statusmessages

    def __call__(self):
        url = self.request.form.get('action_url')
        if not url:
            return self.index()

        (_proto, _host, _path, query, _anchor) = urlsplit(url)
        action = query.split("workflow_action=")[-1].split('&')[0]
        self.context.content_status_modify(action)

        self.messages = self.get_portal_messages()
        self.cancel_redirect()

        return self.index()
