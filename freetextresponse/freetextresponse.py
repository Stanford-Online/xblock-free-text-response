"""
This is the core logic for the Free-text Response XBlock
"""

import os

import pkg_resources
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from enum import Enum
from xblock.core import XBlock
from xblock.fields import Boolean
from xblock.fields import Float
from xblock.fields import Integer
from xblock.fields import List
from xblock.fields import Scope
from xblock.fields import String
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import _


class FreeTextResponse(StudioEditableXBlockMixin, XBlock):
    #  pylint: disable=too-many-ancestors, too-many-instance-attributes
    """
    Enables instructors to create questions with free-text responses.
    """
    @staticmethod
    def workbench_scenarios():
        """
        Gather scenarios to be displayed in the workbench
        """
        scenarios = [
            ('Free-text Response XBlock',
             '''<sequence_demo>
                    <freetextresponse />
                    <freetextresponse
                        display_name="Full Credit is asdf, half is fdsa"
                        fullcredit_keyphrases="['asdf']"
                        halfcredit_keyphrases="['fdsa']"
                    />
                    <freetextresponse
                        display_name="Min words 2"
                        min_word_count="2"
                    />
                    <freetextresponse
                        display_name="Max Attempts 5 XBlock"
                        max_attempts="5"
                    />
                    <freetextresponse
                        display_name="Full credit is asdf, Max Attempts 3"
                        max_attempts="3"
                        fullcredit_keyphrases="['asdf']"
                    />
                    <freetextresponse
                        display_name="New submitted message"
                        submitted_message="Different message"
                    />
                    <freetextresponse
                        display_name="Blank submitted message"
                        submitted_message=""
                    />
                    <freetextresponse
                        display_name="Display correctness if off"
                        display_correctness="False"
                    />
                </sequence_demo>
             '''),
        ]
        return scenarios

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
    display_name = String(
        display_name=_('Display Name'),
        help=_(
            'This is the title for this question type'
        ),
        default=_('Free-text Response'),
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
        default=_('Please enter your response within this text area'),
        scope=Scope.settings,
        multiline_editor=True,
    )
    submitted_message = String(
        display_name=_('Submission Received Message'),
        help=_(
            'This is the message students will see upon '
            'submitting their response'
        ),
        default=_('Your submission has been received'),
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
        default=_(
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

    editable_fields = (
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
    )

    def student_view(self, context=None):
        # pylint: disable=unused-argument
        """
        Build the fragment for the default student view
        """
        view_html = FreeTextResponse.get_resource_string('view.html')
        view_html = view_html.format(
            self=self,
            word_count_message=self._get_word_count_message(),
            indicator_class=self._get_indicator_class(),
            problem_progress=self._get_problem_progress(),
            used_attempts_feedback=self._get_used_attempts_feedback(),
            nodisplay_class=self._get_nodisplay_class(),
            visibility_class=self._get_indicator_visibility_class(),
            submitted_message='',
            user_alert='',
        )
        fragment = self.build_fragment(
            html_source=view_html,
            paths_css=[
                'view.less.min.css',
            ],
            paths_js=[
                'view.js.min.js',
            ],
            fragment_js='FreeTextResponseView',
        )
        return fragment

    @classmethod
    def _generate_validation_message(cls, msg):
        """
        Helper method to generate a ValidationMessage from
        the supplied string
        """
        result = ValidationMessage(
            ValidationMessage.ERROR,
            _(msg)
        )
        return result

    def validate_field_data(self, validation, data):
        """
        Validates settings entered by the instructor.
        """
        if data.weight < 0:
            msg = FreeTextResponse._generate_validation_message(
                'Weight Attempts cannot be negative'
            )
            validation.add(msg)
        if data.max_attempts < 0:
            msg = FreeTextResponse._generate_validation_message(
                'Maximum Attempts cannot be negative'
            )
            validation.add(msg)
        if data.max_word_count < 0:
            msg = FreeTextResponse._generate_validation_message(
                'Maximum Word Count cannot be negative'
            )
            validation.add(msg)
        if data.min_word_count < 1:
            msg = FreeTextResponse._generate_validation_message(
                'Minimum Word Count cannot be less than 1'
            )
            validation.add(msg)
        if data.min_word_count > data.max_word_count:
            msg = FreeTextResponse._generate_validation_message(
                'Minimum Word Count cannot be greater than Max Word Count'
            )
            validation.add(msg)
        if not data.submitted_message:
            msg = FreeTextResponse._generate_validation_message(
                'Submission Received Message cannot be blank'
            )
            validation.add(msg)

    @classmethod
    def get_resource_string(cls, path):
        """
        Retrieve string contents for the file path
        """
        path = os.path.join('public', path)
        resource_string = pkg_resources.resource_string(__name__, path)
        return resource_string.decode('utf8')

    def get_resource_url(self, path):
        """
        Retrieve a public URL for the file path
        """
        path = os.path.join('public', path)
        resource_url = self.runtime.local_resource_url(self, path)
        return resource_url

    def build_fragment(
            self,
            html_source=None,
            paths_css=[],
            paths_js=[],
            urls_css=[],
            urls_js=[],
            fragment_js=None,
    ):
        #  pylint: disable=dangerous-default-value, too-many-arguments
        """
        Assemble the HTML, JS, and CSS for an XBlock fragment
        """
        fragment = Fragment(html_source)
        for url in urls_css:
            fragment.add_css_url(url)
        for path in paths_css:
            url = self.get_resource_url(path)
            fragment.add_css_url(url)
        for url in urls_js:
            fragment.add_javascript_url(url)
        for path in paths_js:
            url = self.get_resource_url(path)
            fragment.add_javascript_url(url)
        if fragment_js:
            fragment.initialize_js(fragment_js)
        return fragment

    def _get_indicator_visibility_class(self):
        """
        Returns the visibility class for the correctness indicator html element
        """
        if self.display_correctness:
            result = ''
        else:
            result = 'hidden'
        return result

    def _get_word_count_message(self, ignore_attempts=False):
        """
        Returns the word count message
        """
        result = ungettext(
            "Your response must be "
            "between {min} and {max} word.",
            "Your response must be "
            "between {min} and {max} words.",
            self.max_word_count,
        ).format(
            min=self.min_word_count,
            max=self.max_word_count,
        )
        return result

    def _get_invalid_word_count_message(self, ignore_attempts=False):
        """
        Returns the invalid word count message
        """
        result = ''
        if (
                (ignore_attempts or self.count_attempts > 0) and
                (not self._word_count_valid())
        ):
            word_count_message = self._get_word_count_message(ignore_attempts=ignore_attempts)
            result = _("Invalid Word Count. {word_count_message}"
            ).format(
                word_count_message=word_count_message,
            )
        return result

    def _get_indicator_class(self):
        """
        Returns the class of the correctness indicator element
        """
        result = 'unanswered'
        if self.display_correctness and self._word_count_valid():
            if self._determine_credit() == Credit.zero:
                result = 'incorrect'
            else:
                result = 'correct'
        return result

    def _word_count_valid(self):
        """
        Returns a boolean value indicating whether the current
        word count of the user's answer is valid
        """
        word_count = len(self.student_answer.split())
        result = (
            word_count <= self.max_word_count and
            word_count >= self.min_word_count
        )
        return result

    @classmethod
    def _is_at_least_one_phrase_present(cls, phrases, answer):
        """
        Determines if at least one of the supplied phrases is
        present in the given answer
        """
        answer = answer.lower()
        matches = [
            phrase.lower() in answer
            for phrase in phrases
        ]
        return any(matches)

    def _get_problem_progress(self):
        """
        Returns a statement of progress for the XBlock, which depends
        on the user's current score
        """
        if self.weight == 0:
            result = ''
        elif self.score == 0.0:
            result = "({})".format(
                ungettext(
                    "{weight} point possible",
                    "{weight} points possible",
                    self.weight,
                ).format(
                    weight=self.weight,
                )
            )
        else:
            scaled_score = self.score * self.weight
            score_string = '{0:g}'.format(scaled_score)
            result = "({})".format(
                ungettext(
                    "{score_string}/{weight} point",
                    "{score_string}/{weight} points",
                    self.weight,
                ).format(
                    score_string=score_string,
                    weight=self.weight,
                )
            )
        return result

    def _compute_score(self):
        """
        Computes and publishes the user's core for the XBlock
        based on their answer
        """
        credit = self._determine_credit()
        self.score = credit.value
        self.runtime.publish(
            self,
            'grade',
            {
                'value': self.score,
                'max_value': Credit.full.value
            }
        )

    def _determine_credit(self):
        #  Not a standard xlbock pylint disable.
        # This is a problem with pylint 'enums and R0204 in general'
        # pylint: disable=redefined-variable-type
        """
        Helper Method that determines the level of credit that
        the user should earn based on their answer
        """
        result = None
        if self.student_answer == '' or not self._word_count_valid():
            result = Credit.zero
        elif not self.fullcredit_keyphrases \
                and not self.halfcredit_keyphrases:
            result = Credit.full
        elif FreeTextResponse._is_at_least_one_phrase_present(
                self.fullcredit_keyphrases,
                self.student_answer
        ):
            result = Credit.full
        elif FreeTextResponse._is_at_least_one_phrase_present(
                self.halfcredit_keyphrases,
                self.student_answer
        ):
            result = Credit.half
        else:
            result = Credit.zero
        return result

    def _get_used_attempts_feedback(self):
        """
        Returns the text with feedback to the user about the number of attempts
        they have used if applicable
        """
        result = ''
        if self.max_attempts > 0:
            result = ungettext(
                'You have used {count_attempts} of {max_attempts} submission',
                'You have used {count_attempts} of {max_attempts} submissions',
                self.max_attempts,
            ).format(
                count_attempts=self.count_attempts,
                max_attempts=self.max_attempts,
            )
        return result

    def _get_nodisplay_class(self):
        """
        Returns the css class for the submit button
        """
        result = ''
        if self.max_attempts > 0 and self.count_attempts >= self.max_attempts:
            result = 'nodisplay'
        return result

    def _get_submitted_message(self):
        """
        Returns the message to display in the submission-received div
        """
        result = ''
        if self._word_count_valid():
            result = self.submitted_message
        return result

    def _get_user_alert(self, ignore_attempts=False):
        """
        Returns the message to display in the user_alert div
        depending on the student answer
        """
        result = ''
        if not self._word_count_valid():
            result = self._get_invalid_word_count_message(ignore_attempts)
        return result

    @XBlock.json_handler
    def submit(self, data, suffix=''):
        # pylint: disable=unused-argument
        """
        Processes the user's submission
        """
        # Fails if the UI submit/save buttons were shut
        # down on the previous sumbisson
        if self.max_attempts == 0 or self.count_attempts < self.max_attempts:
            self.student_answer = data['student_answer']
            if self._word_count_valid():
                self.count_attempts += 1
                self._compute_score()
        result = {
            'status': 'success',
            'problem_progress': self._get_problem_progress(),
            'indicator_class': self._get_indicator_class(),
            'used_attempts_feedback': self._get_used_attempts_feedback(),
            'nodisplay_class': self._get_nodisplay_class(),
            'submitted_message': self._get_submitted_message(),
            'user_alert': self._get_user_alert(
                ignore_attempts=True,
            ),
            'visibility_class': self._get_indicator_visibility_class(),
        }
        return result

    @XBlock.json_handler
    def save_reponse(self, data, suffix=''):
        # pylint: disable=unused-argument
        """
        Processes the user's save
        """
        # Fails if the UI submit/save buttons were shut
        # down on the previous sumbisson
        if self.max_attempts == 0 or self.count_attempts < self.max_attempts:
            self.student_answer = data['student_answer']
        result = {
            'status': 'success',
            'problem_progress': self._get_problem_progress(),
            'indicator_class': self._get_indicator_class(),
            'used_attempts_feedback': self._get_used_attempts_feedback(),
            'nodisplay_class': self._get_nodisplay_class(),
            'submitted_message': '',
            'user_alert': self.saved_message,
            'visibility_class': self._get_indicator_visibility_class(),
        }
        return result


class Credit(Enum):
    # pylint: disable=too-few-public-methods
    """
    An enumeration of the different types of credit a submission can be
    awareded: Zero Credit, Half Credit, and Full Credit
    """
    zero = 0.0
    half = 0.5
    full = 1.0
