"""
This is the core logic for the Free-text Response XBlock
"""
from enum import Enum
from django.db import IntegrityError
from django.template.context import Context
from django.utils.translation import ungettext
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from xblock.core import XBlock
from xblock.fields import Boolean
from xblock.fields import Float
from xblock.fields import Integer
from xblock.fields import List
from xblock.fields import Scope
from xblock.fields import String
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin
from .mixins import EnforceDueDates, MissingDataFetcherMixin


MAX_RESPONSES = 3


@XBlock.needs("i18n")
class FreeTextResponse(
        EnforceDueDates,
        MissingDataFetcherMixin,
        StudioEditableXBlockMixin,
        XBlock,
):
    #  pylint: disable=too-many-ancestors, too-many-instance-attributes
    """
    Enables instructors to create questions with free-text responses.
    """

    loader = ResourceLoader(__name__)

    @staticmethod
    def workbench_scenarios():
        """
        Gather scenarios to be displayed in the workbench
        """
        scenarios = [
            ('Free-text Response XBlock',
             '''<sequence_demo>
                    <freetextresponse />
                    <freetextresponse name='My First XBlock' />
                    <freetextresponse
                        display_name="Full Credit is asdf, half is fdsa"
                        fullcredit_keyphrases="['asdf']"
                        halfcredit_keyphrases="['fdsa']"
                        min_word_count="2"
                        max_word_count="2"
                        max_attempts="5"
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
                        min_word_count="2"
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
        'display_other_student_responses',
        'saved_message',
    )

    def build_fragment(
            self,
            rendered_template,
            initialize_js_func,
            additional_css=[],
            additional_js=[],
    ):
        #  pylint: disable=dangerous-default-value, too-many-arguments
        """
        Creates a fragment for display.
        """
        fragment = Fragment(rendered_template)
        for item in additional_css:
            url = self.runtime.local_resource_url(self, item)
            fragment.add_css_url(url)
        for item in additional_js:
            url = self.runtime.local_resource_url(self, item)
            fragment.add_javascript_url(url)
        fragment.initialize_js(initialize_js_func)
        return fragment

    # Decorate the view in order to support multiple devices e.g. mobile
    # See: https://openedx.atlassian.net/wiki/display/MA/Course+Blocks+API
    # section 'View @supports(multi_device) decorator'
    @XBlock.supports('multi_device')
    def student_view(self, context={}):
        # pylint: disable=dangerous-default-value
        """The main view of FreeTextResponse, displayed when viewing courses.

        The main view which displays the general layout for FreeTextResponse

        Args:
            context: Not used for this view.

        Returns:
            (Fragment): The HTML Fragment for this XBlock, which determines the
            general frame of the FreeTextResponse Question.
        """
        display_other_responses = self.display_other_student_responses
        self.runtime.service(self, 'i18n')
        context.update(
            {
                'display_name': self.display_name,
                'indicator_class': self._get_indicator_class(),
                'nodisplay_class': self._get_nodisplay_class(),
                'problem_progress': self._get_problem_progress(),
                'prompt': self.prompt,
                'student_answer': self.student_answer,
                'is_past_due': self.is_past_due(),
                'used_attempts_feedback': self._get_used_attempts_feedback(),
                'visibility_class': self._get_indicator_visibility_class(),
                'word_count_message': self._get_word_count_message(),
                'display_other_responses': display_other_responses,
                'other_responses': self.get_other_answers(),
            }
        )
        template = self.loader.render_django_template(
            'templates/freetextresponse_view.html',
            context=Context(context),
            i18n_service=self.runtime.service(self, 'i18n'),
        )
        fragment = self.build_fragment(
            template,
            initialize_js_func='FreeTextResponseView',
            additional_css=[
                'public/view.css',
            ],
            additional_js=[
                'public/view.js',
            ],
        )
        return fragment

    def max_score(self):
        """
        Returns the configured number of possible points for this component.
        Arguments:
            None
        Returns:
            float: The number of possible points for this component
        """
        return self.weight

    @classmethod
    def _generate_validation_message(cls, msg):
        """
        Helper method to generate a ValidationMessage from
        the supplied string
        """
        result = ValidationMessage(
            ValidationMessage.ERROR,
            ugettext(unicode(msg))
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

    def _get_indicator_visibility_class(self):
        """
        Returns the visibility class for the correctness indicator html element
        """
        if self.display_correctness:
            result = ''
        else:
            result = 'hidden'
        return result

    def _get_word_count_message(self):
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
            word_count_message = self._get_word_count_message()
            result = ugettext(
                "Invalid Word Count. {word_count_message}"
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
            # No trailing zero and no scientific notation
            score_string = ('%.15f' % scaled_score).rstrip('0').rstrip('.')
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

    def _determine_credit(self):
        #  Not a standard xlbock pylint disable.
        # This is a problem with pylint 'enums and R0204 in general'
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

    def _can_submit(self):
        if self.is_past_due():
            return False
        if self.max_attempts == 0:
            return True
        if self.count_attempts < self.max_attempts:
            return True
        return False

    @XBlock.json_handler
    def submit(self, data, suffix=''):
        # pylint: disable=unused-argument
        """
        Processes the user's submission
        """
        # Fails if the UI submit/save buttons were shut
        # down on the previous sumbisson
        if self._can_submit():
            self.student_answer = data['student_answer']
            # Counting the attempts and publishing a score
            # even if word count is invalid.
            self.count_attempts += 1
            self._compute_score()
            display_other_responses = self.display_other_student_responses
            if display_other_responses and data.get('can_record_response'):
                self.store_student_response()
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
            'other_responses': self.get_other_answers(),
            'display_other_responses': self.display_other_student_responses,
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
            'used_attempts_feedback': self._get_used_attempts_feedback(),
            'nodisplay_class': self._get_nodisplay_class(),
            'submitted_message': '',
            'user_alert': self.saved_message,
            'visibility_class': self._get_indicator_visibility_class(),
        }
        return result

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

    def get_other_answers(self):
        """
        Returns at most MAX_RESPONSES answers from the pool.

        Does not return answers the student had submitted.
        """
        student_id = self.get_student_id()
        display_other_responses = self.display_other_student_responses
        shouldnt_show_other_responses = not display_other_responses
        student_answer_incorrect = self._determine_credit() == Credit.zero
        if student_answer_incorrect or shouldnt_show_other_responses:
            return []
        return_list = [
            response
            for response in self.displayable_answers
            if response['student_id'] != student_id
        ]

        return_list = return_list[-(MAX_RESPONSES):]
        return return_list


class Credit(Enum):
    # pylint: disable=too-few-public-methods
    """
    An enumeration of the different types of credit a submission can be
    awareded: Zero Credit, Half Credit, and Full Credit
    """
    zero = 0.0
    half = 0.5
    full = 1.0
