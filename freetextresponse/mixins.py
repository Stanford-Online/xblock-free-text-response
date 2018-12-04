"""
Mixins for the Free Text Response XBlock
"""
# pylint: disable=too-few-public-methods
import datetime


class EnforceDueDates(object):
    """
    xBlock Mixin to allow xblocks to check the due date
    (taking the graceperiod into account) of the
    subsection in which they are placed
    """

    def is_past_due(self):
        """
        Determine if component is past-due
        """
        # These values are pulled from platform.
        # They are defaulted to None for tests.
        due = getattr(self, 'due', None)
        graceperiod = getattr(self, 'graceperiod', None)
        # Calculate the current DateTime so we can compare the due date to it.
        # datetime.utcnow() returns timezone naive date object.
        now = datetime.datetime.utcnow()
        if due is not None:
            # Remove timezone information from platform provided due date.
            # Dates are stored as UTC timezone aware objects on platform.
            due = due.replace(tzinfo=None)
            if graceperiod is not None:
                # Compare the datetime objects (both have to be timezone naive)
                due = due + graceperiod
            return now > due
        return False


class MissingDataFetcherMixin(object):
    """
    The mixin used for getting the student_id of the current user.
    """
    def get_student_id(self):
        """
        Get the student id.
        """
        if hasattr(self, 'xmodule_runtime'):
            student_id = self.xmodule_runtime.anonymous_student_id
            # pylint:disable=E1101
        else:
            student_id = self.scope_ids.user_id or ''
            student_id = unicode(student_id)
        return student_id
