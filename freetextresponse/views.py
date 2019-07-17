"""
Handle view logic for the XBlock
"""
from __future__ import absolute_import

from six import text_type
from xblock.core import XBlock
from xblock.validation import ValidationMessage
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .mixins.dates import EnforceDueDates
from .mixins.fragment import XBlockFragmentBuilderMixin
from .mixins.i18n import I18nXBlockMixin
from .models import Credit
from .models import MAX_RESPONSES


#  pylint: disable=no-member
class FreeTextResponseViewMixin(
        I18nXBlockMixin,
        EnforceDueDates,
        XBlockFragmentBuilderMixin,
        StudioEditableXBlockMixin,
):
    """
    Handle view logic for FreeTextResponse XBlock instances
    """

    loader = ResourceLoader(__name__)
    static_js_init = 'FreeTextResponseView'

    def provide_context(self, context=None):
        """
        Build a context dictionary to render the student view
        """
        context = context or {}
        context = dict(context)
        context.update({
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
            'display_other_responses': self.display_other_student_responses,
            'other_responses': self.get_other_answers(),
            'user_alert': '',
            'submitted_message': '',
        })
        return context

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

    def _get_nodisplay_class(self):
        """
        Returns the css class for the submit button
        """
        result = ''
        if self.max_attempts > 0 and self.count_attempts >= self.max_attempts:
            result = 'nodisplay'
        return result

    def _word_count_valid(self):
        """
        Returns a boolean value indicating whether the current
        word count of the user's answer is valid
        """
        word_count = len(self.student_answer.split())
        result = self.max_word_count >= word_count >= self.min_word_count
        return result

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
        elif _is_at_least_one_phrase_present(
                self.fullcredit_keyphrases,
                self.student_answer
        ):
            result = Credit.full
        elif _is_at_least_one_phrase_present(
                self.halfcredit_keyphrases,
                self.student_answer
        ):
            result = Credit.half
        else:
            result = Credit.zero
        return result

    def _get_problem_progress(self):
        """
        Returns a statement of progress for the XBlock, which depends
        on the user's current score
        """
        if self.weight == 0:
            result = ''
        elif self.score == 0.0:
            result = "({})".format(
                self.ungettext(
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
                self.ungettext(
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
            result = self.ungettext(
                'You have used {count_attempts} of {max_attempts} submission',
                'You have used {count_attempts} of {max_attempts} submissions',
                self.max_attempts,
            ).format(
                count_attempts=self.count_attempts,
                max_attempts=self.max_attempts,
            )
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

    def _get_word_count_message(self):
        """
        Returns the word count message
        """
        result = self.ungettext(
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
            result = self.ugettext(
                "Invalid Word Count. {word_count_message}"
            ).format(
                word_count_message=word_count_message,
            )
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
        """
        Determine if a user may submit a response
        """
        if self.is_past_due():
            return False
        if self.max_attempts == 0:
            return True
        if self.count_attempts < self.max_attempts:
            return True
        return False

    def _generate_validation_message(self, text):
        """
        Helper method to generate a ValidationMessage from
        the supplied string
        """
        result = ValidationMessage(
            ValidationMessage.ERROR,
            self.ugettext(text_type(text))
        )
        return result

    def validate_field_data(self, validation, data):
        """
        Validates settings entered by the instructor.
        """
        if data.weight < 0:
            msg = self._generate_validation_message(
                'Weight Attempts cannot be negative'
            )
            validation.add(msg)
        if data.max_attempts < 0:
            msg = self._generate_validation_message(
                'Maximum Attempts cannot be negative'
            )
            validation.add(msg)
        if data.min_word_count < 1:
            msg = self._generate_validation_message(
                'Minimum Word Count cannot be less than 1'
            )
            validation.add(msg)
        if data.min_word_count > data.max_word_count:
            msg = self._generate_validation_message(
                'Minimum Word Count cannot be greater than Max Word Count'
            )
            validation.add(msg)
        if not data.submitted_message:
            msg = self._generate_validation_message(
                'Submission Received Message cannot be blank'
            )
            validation.add(msg)


def _is_at_least_one_phrase_present(phrases, answer):
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
