"""
Mixins for the Free Text Response XBlock
"""
import datetime
import pytz
from django.conf import settings

TIME_ZONE = pytz.timezone(getattr(settings, 'TIME_ZONE', pytz.utc.zone))


class EnforceDueDates(object):  # pylint: disable=too-few-public-methods
    """
    xBlock Mixin to allow xblocks to check the due date
    (taking the graceperiod into account) of the
    subsection in which they are placed
    """

    # These values are pulled from platform.
    # They are defaulted to None for tests.
    due = None
    graceperiod = None

    def is_past_due(self):
        """
        Determine if component is past-due
        """
        now = datetime.datetime.utcnow().replace(tzinfo=TIME_ZONE)
        if self.due is not None:
            due_date = self.due
            if self.graceperiod is not None:
                due_date = due_date + self.graceperiod
            return now > due_date
        return False
