"""Module for events classes. """

from ..actions.action_create_template import ActionQuery2
from ..actions.MySQL_SelectQuery import MySQLSelect
from ..actions.action_run_script import ActionQuery3
from ..actions.verify_target import VerifyTargetQuery
from ..constants.basic_constants import BasicConstants


def resolve_event(event_type, options):
    """Return the proper handler based on the event type. """

    if event_type == BasicConstants.VERIFY_TARGET_TYPE:
        handler = VerifyTargetQuery()
    elif event_type == BasicConstants.SELECT_TYPE:
        handler = MySQLSelect()
    elif event_type == BasicConstants.ACTIVITY_2_TYPE:
        handler = ActionQuery2()
    elif event_type == BasicConstants.ACTIVITY_3_TYPE:
        handler = ActionQuery3(options.get_jail_params())
    else:
        return None
    handler.create_logger(options)
    return handler
