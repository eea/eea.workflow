## Controller Python Script "content_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=None, comment='', effective_date="_NOT_SET_", expiration_date="_NOT_SET_", *args
##title=handles the workflow transitions of objects
##
from ZODB.POSException import ConflictError
from DateTime import DateTime
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName

plone_utils = getToolByName(context, 'plone_utils')
contentEditSuccess=0
plone_log=context.plone_log
new_context = context.portal_factory.doCreate(context)
portal_workflow=new_context.portal_workflow
transitions = portal_workflow.getTransitionsFor(new_context)
transition_ids = [t['id'] for t in transitions]

if workflow_action in transition_ids \
   and (not effective_date or effective_date == "_NOT_SET_") \
   and context.EffectiveDate()=='None':
    effective_date = DateTime()

def editContent(obj, effective, expiry):
    kwargs = {}
    if effective != "_NOT_SET_":
        kwargs['effective_date'] = effective
    if expiry != "_NOT_SET_":
        kwargs['expiration_date'] = expiry
    new_context.plone_utils.contentEdit( obj, **kwargs)

#You can transition content but not have the permission to ModifyPortalContent
try:
    editContent(new_context,effective_date,expiration_date)
    contentEditSuccess=1
except (Unauthorized,'Unauthorized'):
    pass

wfcontext = context

# Create the note while we still have access to wfcontext
note = 'Changed status of %s at %s' % (wfcontext.title_or_id(), wfcontext.absolute_url())

if workflow_action in transition_ids:
    wfcontext=new_context.portal_workflow.doActionFor( context,
                                                       workflow_action,
                                                       comment=comment )

if not wfcontext:
    wfcontext = new_context

#The object post-transition could now have ModifyPortalContent permission.
if not contentEditSuccess:
    try:
        editContent(wfcontext, effective_date, expiration_date)
    except (Unauthorized,'Unauthorized'):
        pass

transaction_note(note)

# If this item is the default page in its parent, attempt to publish that
# too. It may not be possible, of course
# we don't touch parent for linguaflow transitions
if plone_utils.isDefaultPage(new_context) and workflow_action not in \
    ['invalidate', 'invalidateall', 'validate', 'validateall', 'nochange']:
    parent = new_context.aq_inner.aq_parent
    try:
        parent.content_status_modify( workflow_action,
                                      comment,
                                      effective_date=effective_date,
                                      expiration_date=expiration_date )
    except ConflictError:
        raise
    except Exception:
        pass

if workflow_action == "fake_publish":
    return state.set(context=wfcontext)

#support for eea.workflow fake_publish and readiness check
#if workflow_action == "fake_publish":
    #msg = u"The workflow transition cannot be executed, the object doesn't meet the requirements. "
    #api = context.restrictedTraverse("@@get_readiness")
    #info = api.get_info_for("published")    #ZZZ: here we hardcode the transition id
    #extra = info['extra']
    #totmiss = info['rfs_required'] - info['rfs_with_value'] - len(info['extra'])
    #msg += "You have %s fields or conditions to fulfil. <br />" % totmiss
    #if info['rfs_field_names']:
        #msg += "<br />The following required fields are not filled in: %s. <br />" % \
               #", ".join([x[1] for x in info['rfs_field_names']])
    #if info['extra']:
        #msg += "<br />The following conditions have not been fulfiled: <br />" + \
            #"<br />".join([x[1] for x in info['extra']])

    ##u"Please follow the guidelines in meeting these requirements", 

    #context.plone_utils.addPortalMessage(msg)
    #return state.set(context=wfcontext)
    

context.plone_utils.addPortalMessage(_(u'Your content\'s status has been modified.'))
return state.set(context=wfcontext)
