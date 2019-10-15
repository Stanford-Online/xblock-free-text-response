"""
Handle data access logic for the XBlock
"""
from __future__ import absolute_import

from enum import Enum
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from xblock.fields import Boolean
from xblock.fields import Float
from xblock.fields import Integer
from xblock.fields import List
from xblock.fields import Scope
from xblock.fields import String


MAX_RESPONSES = 3


class FreeTextResponseModelMixin(object):
    """
    Handle data access for Image Modal XBlock instances
    """

    editable_fields = [
        'display_name',
        'prompt',
        'weight',
        'max_attempts',
        'display_correctness',
        'min_word_count',
        'max_word_count',
        'fullcredit_keyphrases',
        'halfcredit_keyphrases',
        'submitted_message',
        'display_other_student_responses',
        'saved_message',
    ]

    display_correctness = Boolean(
        display_name=_('Display Correctness?'),
        help=_(
            'This is a flag that indicates if the indicator '
            'icon should be displayed after a student enters '
            'their response'
        ),
        default=True,
        scope=Scope.settings,
    )
    display_other_student_responses = Boolean(
        display_name=_('Display Other Student Responses'),
        help=_(
            'This will display other student responses to the '
            'student after they submit their response.'
        ),
        default=False,
        scope=Scope.settings,
    )
    displayable_answers = List(
        default=[],
        scope=Scope.user_state_summary,
        help=_('System selected answers to give to students'),
    )
    display_name = String(
        display_name=_('Display Name'),
        help=_(
            'This is the title for this question type'
        ),
        default='Free-text Response',
        scope=Scope.settings,
    )
    fullcredit_keyphrases = List(
        display_name=_('Full-Credit Key Phrases'),
        help=_(
            'This is a list of words or phrases, one of '
            'which must be present in order for the student\'s answer '
            'to receive full credit'
        ),
        default=[],
        scope=Scope.settings,
    )
    halfcredit_keyphrases = List(
        display_name=_('Half-Credit Key Phrases'),
        help=_(
            'This is a list of words or phrases, one of '
            'which must be present in order for the student\'s answer '
            'to receive half credit'
        ),
        default=[],
        scope=Scope.settings,
    )
    max_attempts = Integer(
        display_name=_('Maximum Number of Attempts'),
        help=_(
            'This is the maximum number of times a '
            'student is allowed to attempt the problem'
        ),
        default=0,
        values={'min': 1},
        scope=Scope.settings,
    )
    max_word_count = Integer(
        display_name=_('Maximum Word Count'),
        help=_(
            'This is the maximum number of words allowed for this '
            'question'
        ),
        default=10000,
        values={'min': 1},
        scope=Scope.settings,
    )
    min_word_count = Integer(
        display_name=_('Minimum Word Count'),
        help=_(
            'This is the minimum number of words required '
            'for this question'
        ),
        default=1,
        values={'min': 1},
        scope=Scope.settings,
    )
    prompt = String(
        display_name=_('Prompt'),
        help=_(
            'This is the prompt students will see when '
            'asked to enter their response'
        ),
        default='Please enter your response within this text area',
        scope=Scope.settings,
        multiline_editor=True,
    )
    submitted_message = String(
        display_name=_('Submission Received Message'),
        help=_(
            'This is the message students will see upon '
            'submitting their response'
        ),
        default='Your submission has been received',
        scope=Scope.settings,
    )
    weight = Integer(
        display_name=_('Weight'),
        help=_(
            'This assigns an integer value representing '
            'the weight of this problem'
        ),
        default=0,
        values={'min': 1},
        scope=Scope.settings,
    )
    saved_message = String(
        display_name=_('Draft Received Message'),
        help=_(
            'This is the message students will see upon '
            'submitting a draft response'
        ),
        default=(
            'Your answers have been saved but not graded. '
            'Click "Submit" to grade them.'
        ),
        scope=Scope.settings,
    )
    count_attempts = Integer(
        default=0,
        scope=Scope.user_state,
    )
    score = Float(
        default=0.0,
        scope=Scope.user_state,
    )
    student_answer = String(
        default='',
        scope=Scope.user_state,
    )
    has_score = True
    show_in_read_only_mode = True

    def store_student_response(self):
        """
        Submit a student answer to the answer pool by appending the given
        answer to the end of the list.
        """
        # if the answer is wrong, do not display it
        if self.score != Credit.full.value:
            return

        student_id = self.get_student_id()
        # remove any previous answers the student submitted
        for index, response in enumerate(self.displayable_answers):
            if response['student_id'] == student_id:
                del self.displayable_answers[index]
                break

        self.displayable_answers.append({
            'student_id': student_id,
            'answer': self.student_answer,
        })

        # Want to store extra response so student can still see
        # MAX_RESPONSES answers if their answer is in the pool.
        response_index = -(MAX_RESPONSES+1)
        self.displayable_answers = self.displayable_answers[response_index:]

    def max_score(self):
        """
        Returns the configured number of possible points for this component.
        Arguments:
            None
        Returns:
            float: The number of possible points for this component
        """
        return self.weight

    def _compute_score(self):
        """
        Computes and publishes the user's core for the XBlock
        based on their answer
        """
        credit = self._determine_credit()
        self.score = credit.value
        try:
            self.runtime.publish(
                self,
                'grade',
                {
                    'value': self.score,
                    'max_value': Credit.full.value
                }
            )
        except IntegrityError:
            pass


class Credit(Enum):
    # pylint: disable=too-few-public-methods
    """
    An enumeration of the different types of credit a submission can be
    awareded: Zero Credit, Half Credit, and Full Credit
    """
    zero = 0.0
    half = 0.5
    full = 1.0
