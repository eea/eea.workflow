""" Workflow scripts module
"""
from Products.statusmessages.interfaces import IStatusMessage

def fake_transition(statechange, **kw):
    """ Fake Transition
    """
    context = statechange.object

    msg = u"The workflow transition cannot be executed, the object doesn't meet the requirements. "
    api = context.restrictedTraverse("@@get_readiness")
    info = api.get_info_for("published")    #ZZZ: here we hardcode the transition id
    extra = info['extra']
    #totmiss = info['rfs_required'] - info['rfs_with_value'] - len(info['extra'])
    #msg += "You have %s fields or conditions to fulfil. <br />" % totmiss
    if info['rfs_field_names']:
        msg += "<br />The following required fields are not filled in: %s. <br />" % \
               ", ".join([x[1] for x in info['rfs_field_names']])
    if info['extra']:
        msg += "<br />The following conditions have not been fulfiled: <br />" + \
            "<br />".join([x[1] for x in info['extra']])

    #u"Please follow the guidelines in meeting these requirements", 

    IStatusMessage(context.REQUEST).add(msg, type='error')
    #context.plone_utils.addPortalMessage(msg)

    return True
