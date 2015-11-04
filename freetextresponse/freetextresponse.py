"""
This is the core logic for the FreeText XBlock
"""

import os
import re

import pkg_resources

from enum import Enum
from xblock.core import XBlock
from xblock.fields import Scope
from xblock.fields import String
from xblock.fields import Integer
from xblock.fields import Float
from xblock.fields import List
from xblock.fragment import Fragment
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext


class FreeTextResponse(XBlock):
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
            ('FreeText XBlock',
             '''<sequence_demo>
                    <freetextresponse />
                    <freetextresponse name='My First XBlock' />
                </sequence_demo>
             '''),
        ]
        return scenarios

    display_name = String(
        default=_('Free-text Response'),
        scope=Scope.settings,
    )
    display_name_help = _('This is the title for this question type')

    prompt = String(
        default=_('Please enter your response within this text area'),
        scope=Scope.settings,
    )
    prompt_help = _(
        'This is the prompt students will see when '
        'asked to enter their response'
    )

    weight = Integer(
        default=1,
        scope=Scope.settings,
    )
    weight_help = _(
        'This assigns an integer value representing '
        'the weight of this problem'
    )

    score = Float(
        default=0.0,
        scope=Scope.user_state,
    )

    max_attempts = Integer(
        default=0,
        scope=Scope.settings,
    )
    max_attempts_help = _(
        'This is the maximum number of times a student '
        'is allowed to attempt the problem'
    )

    display_correctness = String(
        default='True',
        scope=Scope.settings,
    )
    display_correctness_help = _(
        'This is a flag that indicates if the indicator '
        'icon should be displayed after a student enters '
        'their response'
    )

    min_word_count = Integer(
        default=0,
        scope=Scope.settings,
    )
    min_word_count_help = _(
        'This is the minimum number of words required for this '
        'question'
    )

    max_word_count = Integer(
        default=10000,
        scope=Scope.settings,
    )
    max_word_count_help = _(
        'This is the maximum number of words allowed for this '
        'question'
    )

    fullcredit_keyphrases = List(
        default=[],
        scope=Scope.settings,
    )
    fullcredit_keyphrases_help = _(
        'This is a list of words or phrases, one of '
        'which must be present in order for the student\'s answer '
        'to receive full credit'
    )

    halfcredit_keyphrases = List(
        default=[],
        scope=Scope.settings,
    )
    halfcredit_keyphrases_help = _(
        'This is a comma-separated list of words or phrases, one of '
        'which must be present in order for the student\'s answer '
        'to receive half credit'
    )

    student_answer = String(
        default='',
        scope=Scope.user_state,
    )

    count_attempts = Integer(
        default=0,
        scope=Scope.user_state,
    )

    has_score = True

    def student_view(self, context=None):
        # pylint: disable=unused-argument
        """
        Build the fragment for the default student view
        """
        view_html = FreeTextResponse.get_resource_string('view.html')
        view_html = view_html.format(
            self=self,
            indicator_class=self._get_indicator_class(),
            problem_progress=self._get_problem_progress(),
            used_attempts_feedback=self._get_used_attempts_feedback(),
            submit_class=self._get_submit_class(),
            indicator_visibility_class=self._get_indicator_visiblity_class(),
            word_count_message=self._get_word_count_message(),
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
    def _to_comma_separated_string(cls, items):
        """
        Returns a comma-separated string from the supplied list
        """
        result = ', '.join(items)
        return result

    @classmethod
    def _to_list(cls, comma_separated_string):
        """
        Returns a list form the supplied comma-separated string
        """
        result = [
            phrase.strip()
            for phrase in comma_separated_string.split(',')
        ]
        return result

    def studio_view(self, context=None):
        # pylint: disable=unused-argument
        """
        Build the fragment for the edit/studio view
        Implementation is optional.
        """
        edit_html = FreeTextResponse.get_resource_string('edit.html')
        edit_html = edit_html.format(
            self=self,
            fullcredit_keyphrases=FreeTextResponse._to_comma_separated_string(
                self.fullcredit_keyphrases
            ),
            halfcredit_keyphrases=FreeTextResponse._to_comma_separated_string(
                self.halfcredit_keyphrases
            ),
        )
        fragment = self.build_fragment(
            html_source=edit_html,
            paths_css=[
                'edit.less.min.css',
            ],
            paths_js=[
                'edit.js.min.js',
            ],
            fragment_js='FreeTextResponseEdit',
        )
        return fragment

    @XBlock.json_handler
    def studio_view_save(self, data, suffix=''):
        #  pylint: disable=unused-argument
        """
        Save XBlock fields
        Returns: the new field values
        """
        return self._save_studio_data(data)

    @classmethod
    def _extract_whole_number(cls, data, key):
        """
        Attempts to parse a whole number for the value
        for a given key in a dictionary
        """
        result = None
        if key in data:
            try:
                result = int(float(data[key]))
            except ValueError:
                pass
            else:
                if result < 0:
                    result = None
        return result

    def _save_studio_data(self, data):
        """
        Helper method to save the parameters set by the instructor
        for the given instance of the FreeTextResponse XBlock
        """
        if 'display_name' in data:
            self.display_name = data['display_name']

        if 'prompt' in data:
            self.prompt = data['prompt']

        weight = FreeTextResponse._extract_whole_number(data, 'weight')
        if weight is not None:
            self.weight = weight

        max_attempts = FreeTextResponse._extract_whole_number(
            data,
            'max_attempts'
        )
        if max_attempts is not None:
            self.max_attempts = max_attempts

        min_word_count = FreeTextResponse._extract_whole_number(
            data,
            'min_word_count'
        )
        max_word_count = FreeTextResponse._extract_whole_number(
            data,
            'max_word_count'
        )

        if min_word_count is not None and max_word_count is not None:
            if min_word_count <= max_word_count:
                self.min_word_count = min_word_count
                self.max_word_count = max_word_count

        if 'fullcredit_keyphrases' in data:
            self.fullcredit_keyphrases = FreeTextResponse._to_list(
                data['fullcredit_keyphrases']
            )
        if 'halfcredit_keyphrases' in data:
            self.halfcredit_keyphrases = FreeTextResponse._to_list(
                data['halfcredit_keyphrases']
            )

        result = {
            'display_name': self.display_name,
            'prompt': self.prompt,
            'weight': self.weight,
            'max_attempts': self.max_attempts,
            'display_correctness': self.display_correctness,
            'min_word_count': self.min_word_count,
            'max_word_count': self.max_word_count,
            'fullcredit_keyphrases':
                FreeTextResponse._to_comma_separated_string(
                    self.fullcredit_keyphrases
                ),
            'halfcredit_keyphrases':
                FreeTextResponse._to_comma_separated_string(
                    self.halfcredit_keyphrases
                ),
        }
        return result

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

    def _get_indicator_visiblity_class(self):
        """
        Returns the visibility class for the correctness indicator html element
        """
        result = ''
        if re.search('false', self.display_correctness, re.IGNORECASE):
            result = 'hidden'
        return result

    def _get_word_count_message(self):
        """
        Returns the word count message based on the student's answer
        """
        result = ''
        if self.count_attempts > 0 and not self._word_count_valid():
            result = ungettext(
                "Invalid Word Count. Your reponse must be "
                "between {min} and {max} word.",
                "Invalid Word Count. Your reponse must be "
                "between {min} and {max} words.",
                self.max_word_count,
            ).format(
                min=self.min_word_count,
                max=self.max_word_count,
            )
        return result

    def _get_indicator_class(self):
        """
        Returns the class of the correctness indicator element
        """
        result = ''
        if self.student_answer == '':
            if self.count_attempts == 0:
                result = 'unanswered'
            else:
                result = 'incorrect'
        elif (
                self._word_count_valid() and
                (
                    FreeTextResponse._is_at_least_one_phrase_present(
                        self.halfcredit_keyphrases,
                        self.student_answer,
                    )
                    or
                    FreeTextResponse._is_at_least_one_phrase_present(
                        self.fullcredit_keyphrases,
                        self.student_answer,
                    )
                )
        ):
            result = 'correct'
        else:
            result = 'incorrect'
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
        result = ''
        if self.score == 0.0:
            result = ungettext(
                '{weight} point possible',
                '{weight} points possible',
                self.weight,
            ).format(
                weight=self.weight
            )
        else:
            score_string = '{0:g}'.format(self.score)
            result = ungettext(
                score_string + '/' + "{weight} point",
                score_string + '/' + "{weight} points",
                self.weight,
            ).format(
                weight=self.weight
            )
        return result

    def _compute_score(self):
        """
        Computes and publishes the user's core for the XBlock
        based on their answer
        """
        credit = self._determine_credit()
        if credit == Credit.full:
            self.score = self.weight
        elif credit == Credit.half:
            self.score = float(self.weight)/2
        else:
            self.score = 0.0
        self.runtime.publish(
            self,
            'grade',
            {
                'value': self.score,
                'max_value': self.weight
            }
        )

    def _determine_credit(self):
        """
        Helper Method that determines the level of credit that
        the user should earn based on their answer
        """
        result = None
        if self.student_answer == '' or not self._word_count_valid():
            result = Credit.zero
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

    def _get_submit_class(self):
        """
        Returns the css class for the submit button
        """
        result = ''
        if self.max_attempts > 0 and self.count_attempts >= self.max_attempts:
            result = 'nodisplay'
        return result

    @XBlock.json_handler
    def submit(self, data, suffix=''):
        # pylint: disable=unused-argument
        """
        Processes the user's submission
        """
        if self.max_attempts > 0 and self.count_attempts >= self.max_attempts:
            raise StandardError(
                _(
                    'User has already exceeded the '
                    'maximum number of allowed attempts'
                )
            )
        self.student_answer = data['student_answer']
        if self.max_attempts == 0:
            self.count_attempts = 1
        else:
            self.count_attempts += 1
        self._compute_score()
        result = {
            'status': 'success',
            'problem_progress': self._get_problem_progress(),
            'indicator_class': self._get_indicator_class(),
            'used_attempts_feedback': self._get_used_attempts_feedback(),
            'submit_class': self._get_submit_class(),
            'word_count_message': self._get_word_count_message(),
        }
        return result


class Credit(Enum):
    # pylint: disable=too-few-public-methods
    """
    An enumeration of the different types of credit a submission can be
    awareded: Zero Credit, Half Credit, and Full Credit
    """
    zero = 0
    half = 1
    full = 2
