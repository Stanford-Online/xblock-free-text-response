'''
This is the core logic for the FreeText XBlock
'''

import os
import re

import pkg_resources

from enum import Enum
from xblock.core import XBlock
from xblock.fields import Scope
from xblock.fields import String
from xblock.fields import Integer
from xblock.fields import Float
from xblock.fragment import Fragment


class Freetextresponse(XBlock):
    #  pylint: disable=too-many-ancestors, too-many-instance-attributes
    '''
    Enables instructors to create questions with free-text responses.
    '''
    @staticmethod
    def workbench_scenarios():
        '''
        Gather scenarios to be displayed in the workbench
        '''
        return [
            ('FreeText XBlock',
             '''<sequence_demo>
                    <freetextresponse />
                    <freetextresponse name="My First XBlock" />
                </sequence_demo>
             '''),
        ]
    display_name = String(
        default='FreeText XBlock',
        scope=Scope.settings,
        help="This is the title for this question type",
    )
    prompt = String(
        default='Please enter your response within this text area',
        scope=Scope.settings,
        help='This is the prompt students will see when '
             'asked to enter their response',
    )
    weight = Integer(
        default=1,
        scope=Scope.settings,
        help='This assigns an integer value representing '
             'the weight of this problem',
    )
    score = Float(
        default=0.0,
        scope=Scope.user_state,
        help="This is the score of the user",
    )
    max_attempts = Integer(
        default=0,
        scope=Scope.settings,
        help='This is the maximum number of times a student '
             'is allowed to attempt the problem',
    )
    display_correctness = String(
        default='True',
        scope=Scope.settings,
        help='This is a flag that indicates if the indicator '
             'icon should be displayed after a student enters '
             'their response',
    )
    min_word_count = Integer(
        default=0,
        scope=Scope.settings,
        help='This is the minimum number of words required for this question',
    )
    max_word_count = Integer(
        default=10000,
        scope=Scope.settings,
        help='This is the maximum number of words allowed for this question',
    )
    fullcredit_keyphrases = String(
        default='Full-Credit Phrase 1, Full-Credit Phrase 2, '
                'Full-Credit Phrase 3',
        scope=Scope.settings,
        help="This is a comma-separated list of words or phrases, any of "
             "which must be present in order for the student's answer "
             "to receive full credit",
    )
    halfcredit_keyphrases = String(
        default='Half-Credit Phrase 1, Half-Credit Phrase 2, '
                'Half-Credit Phrase 3',
        scope=Scope.settings,
        help="This is a comma-separated list of words or phrases, any of "
             "which must be present in order for the student's answer "
             "to receive half credit",
    )
    student_answer = String(
        default='',
        scope=Scope.user_state,
        help="This is the body of the user's free-text answer",
    )
    num_attempts = Integer(
        default=0,
        scope=Scope.user_state,
        help="This is the number of attempts the user has currently made",
    )
    has_score = True

    def student_view(self, context=None):  # pylint: disable=unused-argument
        '''
        Build the fragment for the default student view
        '''
        view_html = Freetextresponse.get_resource_string('view.html')
        view_html = view_html.format(
            self=self,
            indicator_class=self.get_indicator_class(),
            problem_progress=self.get_problem_progress(),
            used_attempts_feedback=self.get_used_attempts_feedback(),
            submit_class=self.get_submit_class(),
            indicator_visibility_class=self.get_indicator_visiblity_class(),
            word_count_message=self.get_word_count_message(),
        )
        fragment = self.build_fragment(
            html_source=view_html,
            paths_css=[
                'view.less.min.css',
            ],
            paths_js=[
                'view.js.min.js',
            ],
            fragment_js='FreetextresponseView',
        )
        return fragment

    def studio_view(self, context=None):  # pylint: disable=unused-argument
        '''
        Build the fragment for the edit/studio view
        Implementation is optional.
        '''
        edit_html = Freetextresponse.get_resource_string('edit.html')
        edit_html = edit_html.format(
            self=self,
        )
        fragment = self.build_fragment(
            html_source=edit_html,
            paths_css=[
                'edit.less.min.css',
            ],
            paths_js=[
                'edit.js.min.js',
            ],
            fragment_js='FreetextresponseEdit',
        )
        return fragment

    @XBlock.json_handler
    def studio_view_save(self, data, suffix=''):
        #  pylint: disable=unused-argument
        '''
        Save XBlock fields
        Returns: the new field values
        '''
        return self.save_studio_data(data)

    def save_studio_data(self, data):
        '''
        Helper method to save the parameters set by the instructor
        for the given instance of the FreeTextResponse XBlock
        '''
        self.display_name = data['display_name']
        self.prompt = data['prompt']
        if data['weight'] and int(float(data['weight'])) >= 0:
            self.weight = int(float(data['weight']))
        if data['max_attempts'] and int(float(data['max_attempts'])) >= 0:
            self.max_attempts = int(float(data['max_attempts']))
        self.display_correctness = data['display_correctness']
        if data['min_word_count'] and data['max_word_count']:
            if (
                    int(float(data['min_word_count'])) >= 0 and
                    (
                        int(float(data['min_word_count'])) <=
                        int(float(data['max_word_count']))
                    )
            ):
                self.min_word_count = int(float(data['min_word_count']))
            if (
                    int(float(data['max_word_count'])) >= 0 and
                    (
                        int(float(data['max_word_count'])) >=
                        int(float(data['min_word_count']))
                    )
            ):
                self.max_word_count = int(float(data['max_word_count']))
        self.fullcredit_keyphrases = data['fullcredit_keyphrases']
        self.halfcredit_keyphrases = data['halfcredit_keyphrases']
        return {
            'display_name': self.display_name,
            'prompt': self.prompt,
            'weight': self.weight,
            'max_attempts': self.max_attempts,
            'display_correctness': self.display_correctness,
            'min_word_count': self.min_word_count,
            'max_word_count': self.max_word_count,
            'fullcredit_keyphrases': self.fullcredit_keyphrases,
            'halfcredit_keyphrases': self.halfcredit_keyphrases,
        }

    @classmethod
    def get_resource_string(cls, path):
        '''
        Retrieve string contents for the file path
        '''
        path = os.path.join('public', path)
        resource_string = pkg_resources.resource_string(__name__, path)
        return resource_string.decode('utf8')

    def get_resource_url(self, path):
        '''
        Retrieve a public URL for the file path
        '''
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
        '''
        Assemble the HTML, JS, and CSS for an XBlock fragment
        '''
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

    def get_indicator_visiblity_class(self):
        '''
        Returns the visibility class for the correctness indicator html element
        '''
        if re.search('false', self.display_correctness, re.IGNORECASE):
            return 'hidden'
        return ''

    def get_word_count_message(self):
        '''
        Returns the word count message based on the student's answer
        '''
        if self.num_attempts < 1 or self.word_count_valid():
            return ''
        else:
            return "Invalid Word Count. Your reponse must be " \
                   "between {min} and {max} words."\
                .format(
                    min=self.min_word_count,
                    max=self.max_word_count,
                )

    def get_indicator_class(self):
        '''
        Returns the class of the correctness indicator element
        '''
        if self.student_answer == '':
            if self.num_attempts == 0:
                return 'unanswered'
            else:
                return 'incorrect'
        elif (
                self.word_count_valid() and
                (
                    self.phrase_present_in_answer(
                        self.halfcredit_keyphrases
                    )
                    or
                    self.phrase_present_in_answer(
                        self.fullcredit_keyphrases
                    )
                )
        ):
            return 'correct'
        else:
            return 'incorrect'

    def word_count_valid(self):
        '''
        Returns a boolean value indicating whether the current
        word count of the user's answer is valid
        '''
        word_count = len(self.student_answer.split())
        return (
            word_count <= self.max_word_count and
            word_count >= self.min_word_count
        )

    def phrase_present_in_answer(self, phrase_list):
        '''
        Helper method that returns a boolean value indicating
        whether at least one member of the provided phrase list
        is present in the student's answer
        '''
        if re.search(
                '|'.join(
                    [phrase.strip() for phrase in phrase_list.split(',')]
                ),
                self.student_answer,
                re.IGNORECASE
        ):
            return True
        return False

    def get_problem_progress(self):
        '''
        Returns a statement of progress for the XBlock, which depends
        on the user's current score
        '''
        if self.score == 0.0:
            return (
                str(self.weight)
                + ' point'
                + ('s' if (self.weight > 1) else '')
                + ' possible'
            )
        else:
            return (
                str(self.score).replace('.0', '')
                + '/' + str(self.weight)
                + ' point'
                + ('s' if (self.weight > 1) else '')
            )

    def compute_score(self):
        '''
        Computes and publishes the user's core for the XBlock
        based on their answer
        '''
        credit = self.determine_credit()
        if credit == Credit.full:
            self.score = self.weight
        elif credit == Credit.half:
            self.score = float(self.weight)/2
        else:
            self.score = 0.0
        self.runtime.publish(
            self, "grade",
            {
                'value': self.score,
                'max_value': self.weight
            }
        )

    def determine_credit(self):
        '''
        Helper Method that determines the level of credit that
        the user should earn based on their answer
        '''
        if self.student_answer == '' or not self.word_count_valid():
            return Credit.zero
        if self.phrase_present_in_answer(self.fullcredit_keyphrases):
            return Credit.full
        elif self.phrase_present_in_answer(self.halfcredit_keyphrases):
            return Credit.half
        else:
            return Credit.zero

    def get_used_attempts_feedback(self):
        '''
        Returns the text with feedback to the user about the number of attempts
        they have used if applicable
        '''
        if self.max_attempts == 0:
            return ''
        return (
            'You have used '
            + str(self.num_attempts)
            + ' of '
            + str(self.max_attempts)
            + ' submissions'
        )

    def get_submit_class(self):
        '''
        Returns the css class for the submit button
        '''
        if self.max_attempts > 0 and self.num_attempts >= self.max_attempts:
            return 'nodisplay'
        else:
            return ''

    @XBlock.json_handler
    def submit(self, data, suffix=''):  # pylint: disable=unused-argument
        '''
        Processes the user's submission
        '''
        if self.max_attempts > 0 and self.num_attempts >= self.max_attempts:
            raise StandardError(
                'User has already exceeded the '
                'maximum number of allowed attempts'
            )
        self.student_answer = data['student_answer']
        if self.max_attempts > 0:
            self.num_attempts += 1
        self.compute_score()
        return {
            'status': 'success',
            'problem_progress': self.get_problem_progress(),
            'indicator_class': self.get_indicator_class(),
            'used_attempts_feedback': self.get_used_attempts_feedback(),
            'submit_class': self.get_submit_class(),
            'word_count_message': self.get_word_count_message(),
        }


class Credit(Enum):  # pylint: disable=too-few-public-methods
    '''
    An enumeration of the different types of credit a submission can be
    awareded: Zero Credit, Half Credit, and Full Credit
    '''
    zero = 0
    half = 1
    full = 2
