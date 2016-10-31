"""
This is the core logic for the Free-text Response XBlock
"""


import pkg_resources
import os
from enum import Enum

from xblock.core import XBlock
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblock.fields import Scope, Boolean, String, Float, Integer, List
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext


# Helper class
class Credit(Enum):
    # pylint: disable=too-few-public-methods
    """
    An enumeration of the different types of credit a submission can be
    awareded: Zero Credit, Half Credit, and Full Credit
    """
    zero = 0.0
    half = 0.5
    full = 1.0


class FreeTextResponse(StudioEditableXBlockMixin, XBlock):
    #  pylint: disable=too-many-ancestors, too-many-instance-attributes
    # pylint: disable=R0904
    """
    Enables instructors to create questions with free-text responses.
    """

    # Instructor Facing Editable Fields
    display_name = String(
        display_name=_('Display Name'),
        help=_(
            'This is the title for this question type'
        ),
        default=_('Free-text Response'),
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
    fullcredit_keyphrases = List(
        display_name=_('Full-Credit Key Phrases'),
        help=_(
            'This is a list of words or phrases, one of '
            'which must be present in order for the student\'s answer '
            'to receive full credit. '
            'List may contain dictionaries with phrase, hints '
            'and feedback keys. '
            'Example: '
            '{ '
            ' "phrase": "Answer phrase", '
            ' "feedback": "User feedback" '
            '}, '
            '{ '
            ' "phrase": "Another answer phrase", '
            ' "feedback": "With user feedback" '
            '}'
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
    zerocredit_keyphrases = List(
        display_name=_('Zero-Credit Key Phrases'),
        help=_(
            'This is a list of common incorrect '
            'words or phrases to provide constructive '
            'feedback to the user'
        ),
        default=[],
        scope=Scope.settings,
    )
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
    hints = List(
        display_name=_('Hint Phrases'),
        help=_(
            'This is a list of hints to display to the '
            'user'
        ),
        default=[],
        scope=Scope.settings,
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

    # Not instructor facing fields
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
    hint_counter = Integer(
        default=0,
        scope=Scope.user_state,
    )

    has_score = True

    editable_fields = (
        'display_name',
        'prompt',
        # Minutes allowed
        'max_attempts',
        'weight',
        # Randomization
        # Show Answer
        # Show Reset
        # Timer Between Attempts
        # Minutes Before Warning
        'fullcredit_keyphrases',
        'halfcredit_keyphrases',
        'zerocredit_keyphrases',
        'hints',
        'display_correctness',
        'min_word_count',
        'max_word_count',
        'submitted_message',
    )

    # Editable Field Validation
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

    # Scoring
    def _compute_score(self):
        """
        Computes and publishes the user's core for the XBlock
        based on their answer
        """
        credit = self._determine_credit()
        #pylint: disable=maybe-no-member
        self.score = credit.value
        #pylint: disable=maybe-no-member
        self.runtime.publish(
            self,
            'grade',
            {
                'value': self.score,
                'max_value': Credit.full.value
            }
        )

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

    def _determine_credit(self):
        """
        Helper Method that determines the level of credit that
        the user should earn based on their answer
        """
        result = None
        # Get phrases
        fullcredit_keyphrases = []
        for item in self.fullcredit_keyphrases:
            if 'dict' == type(item).__name__:
                phrase = item.get('phrase', self.fullcredit_keyphrases)
                fullcredit_keyphrases.append(phrase)
            else:
                fullcredit_keyphrases.append(item)
        halfcredit_keyphrases = []
        for item in self.halfcredit_keyphrases:
            if 'dict' == type(item).__name__:
                phrase = item.get('phrase', self.halfcredit_keyphrases)
                halfcredit_keyphrases.append(phrase)
            else:
                halfcredit_keyphrases.append(item)
        # Determine Credit
        if not self.fullcredit_keyphrases \
                and not self.halfcredit_keyphrases:
            # No full or half credit answers specified
            result = Credit.full
        elif FreeTextResponse._is_at_least_one_phrase_present(
                fullcredit_keyphrases,
                self.student_answer
        ):
            result = Credit.full
        elif FreeTextResponse._is_at_least_one_phrase_present(
                halfcredit_keyphrases,
                self.student_answer
        ):
            result = Credit.half
        else:
            result = Credit.zero
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

    # Messages to Student
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

    def _get_submitted_message(self, feedback_text=''):
        """
        Returns the message to display in the submission-received div
        """
        result = ''
        if self._word_count_valid() and not feedback_text:
            result = self.submitted_message
        return result

    @classmethod
    def _get_feedback_if_phrase_present(cls, phrase_dicts, answer):
        """
        Determines if at least one of the supplied phrases is
        present and returns feedback if it exists
        """
        answer = answer.lower()
        for item in phrase_dicts:
            if 'dict' == type(item).__name__:
                phrase = item.get('phrase', None)
                feedback = item.get('feedback', None)
                if phrase and phrase.lower() in answer:
                    # Answer match
                    return feedback
            elif item.lower() in answer:
                # Answer match but no feedback
                break

    def _get_feedback(self):
        """
        Returns the feedback message for a user submission
        Feedback may not exists for answer but may still be
        full, half, or zero credit
        """
        feedback_label = ''
        feedback_text = ''
        # Use score to set feedback label and keyphrases
        keyphrases = self.zerocredit_keyphrases
        if self.score == Credit.full.value:
            feedback_label = 'Correct:'
            keyphrases = self.fullcredit_keyphrases
        elif self.score == Credit.half.value:
            feedback_label = 'Correct:'
            keyphrases = self.halfcredit_keyphrases
        elif self.score == Credit.zero.value:
            feedback_label = 'Incorrect:'
        # Find feedback if it exists in keyphrases
        feedback_text = FreeTextResponse._get_feedback_if_phrase_present(
            keyphrases,
            self.student_answer,
        )
        # Clear label if feedback DNE
        if not feedback_text:
            return ('', '')
        else:
            return (feedback_label, feedback_text)

    def _get_hint_text(self):
        """
        Returns a hint message to display in the user
        """
        result = ''
        hints_total = len(self.hints)
        if 0 < hints_total:
            hint_mod = self.hint_counter % hints_total
            result = _(
                "Hint ({hint_number} of {hints_total}):"
                "{hint}",
            ).format(
                hint_number=hint_mod + 1,
                hints_total=hints_total,
                hint=self.hints[hint_mod],
            )
            self.hint_counter += 1
        return result

    def _get_user_alert(self, ignore_attempts=False):
        """
        Returns the message to display in the user_alert div
        """
        result = ''
        if not self._word_count_valid():
            result = self._get_word_count_message(ignore_attempts)
        return result

    def _get_word_count_message(self, ignore_attempts=False):
        """
        Returns the word count message based on the student's answer
        """
        result = ''
        if (
                (ignore_attempts or self.count_attempts > 0) and
                (not self._word_count_valid())
        ):
            result = ungettext(
                "Invalid Word Count. Your response must be "
                "between {min} and {max} word.",
                "Invalid Word Count. Your response must be "
                "between {min} and {max} words.",
                self.max_word_count,
            ).format(
                min=self.min_word_count,
                max=self.max_word_count,
            )
        return result

    # CSS Classes
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

    def _get_indicator_visibility_class(self):
        """
        Returns the visibility class for the correctness indicator html element
        """
        if self.display_correctness:
            result = ''
        else:
            result = 'hidden'
        return result

    def _get_submitdisplay_class(self):
        """
        Returns the css class for the submit and save buttons
        """
        result = ''
        if self.max_attempts > 0 and self.count_attempts >= self.max_attempts:
            result = 'nodisplay'
        return result

    def _get_hintdisplay_class(self):
        """
        Returns the css class for the hint button
        """
        result = 'nodisplay'
        if 0 < len(self.hints):
            result = ''
        return result

    # Default View
    @classmethod
    def _get_resource_string(cls, path):
        """
        Retrieve string contents for the file path
        """
        path = os.path.join('public', path)
        resource_string = pkg_resources.resource_string(__name__, path)
        return resource_string.decode('utf8')

    def _get_resource_url(self, path):
        """
        Retrieve a public URL for the file path
        """
        path = os.path.join('public', path)
        resource_url = self.runtime.local_resource_url(self, path)
        return resource_url

    def student_view(self, context=None):
        # pylint: disable=unused-argument
        """
        Build the fragment for the default student view
        """
        html = self._get_resource_string('view.html')
        frag = Fragment(
            html.format(
                self=self,
                # Message/Labels
                problem_progress=self._get_problem_progress(),
                used_attempts_feedback=self._get_used_attempts_feedback(),
                submitted_message='',
                feedback_label='',
                feedback_text='',
                hint_text='',
                user_alert='',
                # CSS Classes
                indicator_class=self._get_indicator_class(),
                visibility_class=self._get_indicator_visibility_class(),
                submitdisplay_class=self._get_submitdisplay_class(),
                hintdisplay_class=self._get_hintdisplay_class(),
                # Feedback display class?
            )
        )
        frag.add_css_url(self._get_resource_url("view.less.min.css"))
        frag.add_javascript_url(self._get_resource_url("view.js.min.js"))
        frag.initialize_js('FreeTextResponseView')
        return frag

    # Handlers to perform actions
    @XBlock.json_handler
    def submit(self, data, suffix=''):
        # pylint: disable=unused-argument
        """
        Processes the user's submission
        """
        feedback_label = ''
        feedback_text = ''
        if self.max_attempts == 0 or self.count_attempts < self.max_attempts:
            self.student_answer = data['student_answer']
            # Answers that do not meet min/max word count specifications
            # or are blank submissions(since default word count is one)
            # are not considered for scoring.
            if self._word_count_valid():
                self.count_attempts += 1
                self._compute_score()
                # Find feedback it exists for the answer
                (feedback_label, feedback_text) = self._get_feedback()
        result = {
            'status': 'success',
            # Message/Labels
            'problem_progress': self._get_problem_progress(),
            'used_attempts_feedback': self._get_used_attempts_feedback(),
            'submitted_message': self._get_submitted_message(
                feedback_text,
            ),
            'feedback_label': feedback_label,
            'feedback_text': feedback_text,
            'user_alert': self._get_user_alert(
                ignore_attempts=True,
            ),
            # CSS Classes
            'indicator_class': self._get_indicator_class(),
            'visibility_class': self._get_indicator_visibility_class(),
            'submitdisplay_class': self._get_submitdisplay_class(),
        }
        return result

    @XBlock.json_handler
    def save_response(self, data, suffix=''):
        # pylint: disable=unused-argument
        """
        Processes the user's save
        """
        if self.max_attempts == 0 or self.count_attempts < self.max_attempts:
            self.student_answer = data['student_answer']
        result = {
            'status': 'success',
            # Message/Labels
            # Clear this message on save
            'submitted_message': '',
            'user_alert': self.saved_message,
            # CSS Classes
            'visibility_class': self._get_indicator_visibility_class(),
            'submitdisplay_class': self._get_submitdisplay_class(),
        }
        return result

    @XBlock.json_handler
    def hint_reponse(self, data, suffix=''):
        # pylint: disable=unused-argument
        """
        Returns a hint message if it exists
        does not
        """
        result = {
            'status': 'success',
            'hint_text': self._get_hint_text(),
        }
        return result

    # Workbench
    @staticmethod
    def workbench_scenarios():
        """
        Gather scenarios to be displayed in the workbench
        """
        scenarios = [
            ('Free-text Response XBlock',
             '''<sequence_demo>
                    <freetextresponse
                        display_name="Hints and Feedback"
                        prompt="Which U.S. state has the largest land area?"
                        max_attempts="20"
                        weight="2"
                        fullcredit_keyphrases="[
                            {
                                'phrase':'Alaska',
                                'feedback':'Alaska is 576,400 square miles,
                                    more than double the land area of the
                                    second largest state, Texas.'
                            },
                            {
                                'phrase':'The Last Frontier',
                                'feedback':'Alaska, a.k.a. The Last Frontier,
                                    is 576,400 square miles, more than double
                                    the land area of the second largest state,
                                    Texas.'
                            }

                        ]"
                        halfcredit_keyphrases="[
                            {
                                'phrase':'Texas',
                                'feedback':'While many people think Texas is
                                    the largest state, it is actually the
                                    second largest, with 261,797 square miles.'
                            },
                            {
                                'phrase':'The Lone Star State',
                                'feedback':'While many people think Texas,
                                    a.k.a. The Lone Star State,  is the largest
                                    state, it is actually the second largest,
                                    with 261,797 square miles.'
                            },
                            {
                                'phrase':'Pizza',
                            },
                            'Tacos'
                        ]"
                        zerocredit_keyphrases="[
                            {
                                'phrase':'California',
                                'feedback':'California is the third largest
                                    state, with 155,959 square miles.'
                            },
                            {
                                'phrase':'Pittsburgh',
                                'feedback':'Pittsburgh is not a state.'
                            }
                        ]"
                        hints="[
                            'Consider the square miles, not population.',
                            'Consider all 50 states, not just the continental
                                United States.'
                        ]"
                    />
                    <freetextresponse />
                    <freetextresponse
                        display_name="Full Credit is
                            'The quick brown fox',
                            half is 'The slow wet begal'"
                        fullcredit_keyphrases="['The quick brown fox']"
                        halfcredit_keyphrases="['The slow wet begal']"
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
