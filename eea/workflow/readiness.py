""" Readiness module => readiness for doing a certain transition
"""
from eea.workflow.interfaces import IValueProvider, IObjectReadiness, \
        IFieldIsRequiredForState
from zope.component import getMultiAdapter
from zope.interface import implements

OTHER_METADATA_FIELDS = (
        'locallyAllowedTypes',
        'immediatelyAddableTypes',
        'id',
        'constrainTypesMode',
        )


class ObjectReadiness(object):
    """Provides information about the readiness for doing a certain transition

    An object can have field that are required to be filled in before a workflow transition
    is available for it. To implement this we look for a 'required_for_YYY' boolean,
    where YYY is the workflow state to which we want to transition.
    In addition, if this attribute is missing, we try to call a method "required_for"
    on the field, which receives the object instance and state name as parameters.
    """

    implements(IObjectReadiness)

    checks = {
            # #This is the format:
            #'published':(
            #   ('some title', lambda o:False, 'Some error message'),
            #   )
            }
    # a list of objects whose readiness should be taken into account
    depends_on = None
    def __init__(self, context):
        self.context = context

    def get_info_for(self, state_name):
        """ Get info for state_name
        """

        #Terminology: RFS = required for state ZZZ

        depends_on = self.depends_on or []
        extras = []
        checks = self.checks.get(state_name, [])

        rfs_required   = 0 + len(checks) #the number of fields that are RFS
        rfs_with_value = 0 #the fields RFS that are filled in
        optional_empty = 0 #fields that are not RFS and are not filled in
        total_fields   = 0 #the grand total of fields
        rfs_done       = 0 #the percentage of fields RFS that are filled in
        rfs_field_names = []    #the names of fields that are RFS but 
                                                           # have no value
        rfs_done_field_names = []   #the names of fields that are RFS and 
                                                                #have a value
        optional_with_value = []    #optional fields that have a value
        _debug_fieldnames = []

        for field in self.context.schema.fields():  #we assume AT here
            if field.isMetadata or (field.getName() in OTHER_METADATA_FIELDS):
                continue

            _debug_fieldnames.append(field.getName())

            total_fields += 1

            info = getMultiAdapter([self.context, field],
                                            interface=IValueProvider)
            has_value = info.has_value(state=state_name)

            required_for = getMultiAdapter((self.context, field),
                                            interface=IFieldIsRequiredForState)
            is_needed = required_for(state_name)

            if is_needed:
                rfs_required += 1
                if has_value:
                    rfs_with_value += 1
                    rfs_done_field_names.append((field.getName(),
                                                        field.widget.label))
                else:
                    rfs_field_names.append((field.getName(),
                                                        field.widget.label))
            else:
                if not has_value:
                    optional_empty += 1
                else:
                    optional_with_value.append((field.getName(),
                                                         field.widget.label))

        for checker, error in checks:
            if checker(self.context):
                extras.append(('error', error))
            else:
                rfs_with_value += 1

        #We calculate the stats for the dependencies
        for part in depends_on:
            _info = IObjectReadiness(part).get_info_for(state_name)
            rfs_required += _info['rfs_required']
            rfs_with_value += _info['rfs_with_value']
            total_fields += _info['total_fields']
            rfs_field_names += map(
                    lambda t:(t[0] + "_" + part.getId(), t[1]),
                                                    _info['rfs_field_names'])
            rfs_done_field_names += map(
                    lambda t:(t[0] + "_" + part.getId(), t[1]),
                                                _info['rfs_done_field_names'])

        #rfs_required or 1  #->avoids division by 0
        rfs_done = int(float(rfs_with_value) / float(rfs_required or 1) * 100.0)

        return {
                'rfs_done':rfs_done,
                'rfs_with_value':rfs_with_value,
                'rfs_required':rfs_required,
                'optional_empty':optional_empty,
                'total_fields':total_fields,
                'rfs_field_names':rfs_field_names,
                'rfs_done_field_names':rfs_done_field_names,
                'optional_with_value':optional_with_value,
                'extra':extras,  #extra messages that will be displayed in the
                                                # portlet, in the form of tuples
                'conditions':len(checks),
                '_debug_fieldnames':_debug_fieldnames,
                }

    def is_ready_for(self, state_name):
        """ Is object ready for state_name
        """
        info = self.get_info_for(state_name)
        if info['rfs_required'] == info['rfs_with_value']:
            return True

        return False


class ObjectReadinessView(object):
    """ ObjectReadinessView
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_info_for(self, state_name):
        """ Get info for state name
        """
        return IObjectReadiness(self.context).get_info_for(state_name)

    def is_ready_for(self, state_name):
        """ Is object ready for state name
        """
        return IObjectReadiness(self.context).is_ready_for(state_name)

