"""
Extend XBlock with additional user functionality
"""
from six import text_type


# pylint: disable=too-few-public-methods
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
            student_id = text_type(student_id)
        return student_id
