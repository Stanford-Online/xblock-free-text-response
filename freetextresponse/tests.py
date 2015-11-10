"""
Module Placeholder Docstring
"""
import unittest

import mock
from django.test.client import Client
from django.utils.translation import ugettext as _
from mock import MagicMock
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xblock.field_data import DictFieldData

from .freetextresponse import Credit
from .freetextresponse import FreeTextResponse


class FreetextResponseXblockTestCase(unittest.TestCase):
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
    A complete suite of unit tests for the FreeTextXBlock
    """
    @classmethod
    def make_an_xblock(cls, **kw):
        """
        Helper method that creates a FreeTextResponse XBlock
        """
        course_id = SlashSeparatedCourseKey('foo', 'bar', 'baz')
        runtime = mock.Mock(course_id=course_id)
        scope_ids = mock.Mock()
        field_data = DictFieldData(kw)
        xblock = FreeTextResponse(runtime, field_data, scope_ids)
        xblock.xmodule_runtime = runtime
        return xblock

    def setUp(self):
        self.xblock = FreetextResponseXblockTestCase.make_an_xblock()
        self.client = Client()
        self.test_display_name = 'test_display_name',
        self.test_prompt = 'test_prompt'
        self.test_weight = 5
        self.test_max_attempts = 10
        self.test_display_correctness = 'True'
        self.test_min_word_count = 5
        self.test_max_word_count = 10
        self.test_fullcredit_keyphrases = 'test fullcredit phrase 1, ' \
                                          'test fullcredit phrase 2'
        self.test_halfcredit_keyphrases = 'test halfcredit phrase 1, ' \
                                          'test halfcredit phrase 2'
        self.test_student_answer = 'test student answer'
        self.test_count_attempts = '3'

    def test_student_view(self):
        # pylint: disable=protected-access
        """
        Checks the student view for student specific instance variables.
        """
        student_view_html = self.student_view_html()
        self.assertIn(self.xblock.display_name, student_view_html)
        self.assertIn(self.xblock.prompt, student_view_html)
        self.assertIn(self.xblock._get_indicator_class(), student_view_html)
        self.assertIn(self.xblock._get_problem_progress(), student_view_html)

    def test_studio_view(self):
        """
        Checks studio view for instance variables specified by the instructor.
        """
        studio_view_html = self.studio_view_html()
        self.assertIn(self.xblock.display_name, studio_view_html)
        self.assertIn(self.xblock.prompt, studio_view_html)
        self.assertIn(str(self.xblock.max_attempts), studio_view_html)
        self.assertIn(str(self.xblock.display_correctness), studio_view_html)
        self.assertIn(str(self.xblock.min_word_count), studio_view_html)
        self.assertIn(str(self.xblock.max_word_count), studio_view_html)
        self.assertIn(
            ', '.join(
                self.xblock.fullcredit_keyphrases
            ),
            studio_view_html
        )
        self.assertIn(
            ', '.join(
                self.xblock.halfcredit_keyphrases
            ),
            studio_view_html
        )

    def test_initialization_variables(self):
        """
        Checks that all instance variables are initialized correctly
        """
        self.assertEquals('Free-text Response', self.xblock.display_name)
        self.assertEquals(
            'Please enter your response within this text area',
            self.xblock.prompt
        )
        self.assertEquals(0.0, self.xblock.score)
        self.assertEquals(0, self.xblock.max_attempts)
        self.assertTrue(self.xblock.display_correctness)
        self.assertEquals(0, self.xblock.min_word_count)
        self.assertEquals(10000, self.xblock.max_word_count)
        self.assertEquals(
            [],
            self.xblock.fullcredit_keyphrases
        )
        self.assertEquals(
            [],
            self.xblock.halfcredit_keyphrases
        )
        self.assertEquals('', self.xblock.student_answer)
        self.assertEquals(0, self.xblock.count_attempts)

    def student_view_html(self):
        """
        Helper method that returns the html of student_view
        """
        return self.xblock.student_view().content

    def studio_view_html(self):
        """
        Helper method that returns the html of studio_view
        """
        return self.xblock.studio_view(context=None).content

    def test_word_count_message_blank_when_attempts_0(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the word count message is blank when the
        user has made zero attempts
        """
        self.xblock.count_attempts = 0
        self.assertEquals('', self.xblock._get_word_count_message())

    def test_word_count_message_blank_when_word_count_valid(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the word count message doesn't display when
        the word count is valid
        """
        self.xblock.count_attempts = 5
        self.xblock._word_count_valid = MagicMock(return_value=True)
        self.assertEquals('', self.xblock._get_word_count_message())

    def test_invalid_word_count_message(self):
        # pylint: disable=protected-access
        """
        Tests that the invalid word count message displays
        when appropriate
        """
        self.xblock.count_attempts = 5
        self.xblock._word_count_valid = MagicMock(return_value=False)
        self.assertIn(
            _('Invalid Word Count. Your reponse must be between'),
            self.xblock._get_word_count_message()
        )

    def test_indicator_class_unanswered(self):
        # pylint: disable=protected-access
        """
        Tests that the 'unanswered' class for the display_correctness
        html component displays when appropriate
        """
        self.xblock.student_answer = ''
        self.xblock.count_attempts = 0
        self.assertEquals('unanswered', self.xblock._get_indicator_class())

    def test_indicator_class_incorrect_blank_response(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the 'incorrect' class for the display_correctness html
        component displays when the response is blank
        """
        self.xblock.student_answer = ''
        self.xblock.count_attempts = 5
        self.assertEquals('incorrect', self.xblock._get_indicator_class())

    def test_indicator_class_incorrect_normal_response(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the 'incorrect' class for the display_correctness
        html component displays when the response is incorrect
        """
        self.xblock.student_answer = 'Non-blank response'
        self.xblock.count_attempts = 5
        self.xblock._word_count_valid = MagicMock(return_value=False)
        original = FreeTextResponse._is_at_least_one_phrase_present
        FreeTextResponse._is_at_least_one_phrase_present = \
            MagicMock(return_value=False)
        self.assertEquals('incorrect', self.xblock._get_indicator_class())
        FreeTextResponse._is_at_least_one_phrase_present = original

    def test_indicator_class_correct_normal_response(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the 'correct' class for the display_correctness html
        component displays when the response is correct
        """
        self.xblock.student_answer = 'Non-blank response'
        self.xblock.count_attempts = 5
        self.xblock._word_count_valid = MagicMock(return_value=True)
        original = FreeTextResponse._is_at_least_one_phrase_present
        FreeTextResponse._is_at_least_one_phrase_present = \
            MagicMock(return_value=True)
        self.assertEquals('correct', self.xblock._get_indicator_class())
        FreeTextResponse._is_at_least_one_phrase_present = original

    def test_word_count_in_range(self):
        # pylint: disable=protected-access
        """
        Tests that the word_count_valid method returns the
        appropriate response when the word count is valid
        """
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 1
        self.xblock.max_word_count = 5
        self.assertTrue(self.xblock._word_count_valid())

    def test_word_count_min(self):
        # pylint: disable=protected-access
        """
        Tests that the word_count_valid method returns the
        appropriate response when the student's answer has
        the minimum number of permissible words
        """
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 3
        self.xblock.max_word_count = 5
        self.assertTrue(self.xblock._word_count_valid())

    def test_word_count_max(self):
        # pylint: disable=protected-access
        """
        Tests that the word_count_valid method returns the
        appropriate response when the student's answer has
        the maximum number of permissible words
        """
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 0
        self.xblock.max_word_count = 3
        self.assertTrue(self.xblock._word_count_valid())

    def test_word_count_too_short(self):
        # pylint: disable=protected-access
        """
        Tests that the word_count_valid method returns the
        appropriate response when the student's answer
        is too short
        """
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 4
        self.xblock.max_word_count = 5
        self.assertFalse(self.xblock._word_count_valid())

    def test_word_count_too_long(self):
        # pylint: disable=protected-access
        """
        Tests that the word_count_valid method returns the
        appropriate response when the student's answer
        is too long
        """
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 0
        self.xblock.max_word_count = 2
        self.assertFalse(self.xblock._word_count_valid())

    def test_phrase_present_in_answer(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests the phrase_present_in_answer helper method, when at least
        of of the phrases is present in the answer
        """
        phrases = ["Battle Ends", "And", "Down", "Goes", "Charles' Father"]
        answer = "chArles' fAther"
        self.assertEqual(
            True,
            FreeTextResponse._is_at_least_one_phrase_present(
                phrases, answer
            )
        )

    def test_pattern_not_present_in_answer(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests the phrase_present_in_answer helper method, when none of the
        phrases are present in the anaswer
        """
        phrases = ["Battle Ends", "And", "Down", "Goes", "Charles' Father"]
        answer = "cHarleS' mother went to the store to buy honey"
        self.assertFalse(
            FreeTextResponse._is_at_least_one_phrase_present(
                phrases,
                answer
            )
        )

    def test_problem_progress_score_zero_weight_singular(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is singular, and the score is zero
        """
        self.xblock.score = 0
        self.xblock.weight = 1
        self.assertEquals(
            _('1 point possible'),
            self.xblock._get_problem_progress()
        )

    def test_problem_progress_score_zero_weight_plural(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is plural, and the score is zero
        """
        self.xblock.score = 0
        self.xblock.weight = 3
        self.assertEquals(
            _('3 points possible'),
            self.xblock._get_problem_progress()
        )

    def test_problem_progress_score_positive_weight_singular(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is singular, and the score is positive
        """
        self.xblock.score = 1
        self.xblock.weight = 1
        self.assertEquals(_('1/1 point'), self.xblock._get_problem_progress())

    def test_problem_progress_score_positive_weight_plural(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is plural, and the score is positive
        """
        self.xblock.score = 1.5
        self.xblock.weight = 3
        self.assertEquals(
            _('1.5/3 points'),
            self.xblock._get_problem_progress()
        )

    def test_compute_score_full_credit(self):
        # pylint: disable=protected-access
        """
        Tests that a full-credit grade is assigned when appropriate
        """
        def get_full_credit():
            """
            Side-effect that returns full credit
            """
            return Credit.full
        self.xblock.runtime.publish = MagicMock(return_value=None)
        self.xblock._determine_credit = MagicMock(side_effect=get_full_credit)
        self.xblock.weight = 5
        self.xblock._compute_score()
        self.xblock.runtime.publish.assert_called_with(
            self.xblock,
            'grade',
            {'value': 5.0, 'max_value': 5}
        )

    def test_compute_score_half_credit(self):
        # pylint: disable=protected-access
        """
        Tests that a half-credit grade is assigned when appropriate
        """
        def get_half_credit():
            """
            Side-effect that returns half credit
            """
            return Credit.half
        self.xblock.runtime.publish = MagicMock(return_value=None)
        self.xblock._determine_credit = MagicMock(side_effect=get_half_credit)
        self.xblock.weight = 5
        self.xblock._compute_score()
        self.xblock.runtime.publish.assert_called_with(
            self.xblock,
            'grade',
            {'value': 2.5, 'max_value': 5}
        )

    def test_compute_score_no_credit(self):
        # pylint: disable=protected-access
        """
        Tests that a no-credit grade is assigned when appropriate
        """
        def get_no_credit():
            """
            Side-effect that returns no credit
            """
            return Credit.zero
        self.xblock.runtime.publish = MagicMock(return_value=None)
        self.xblock._determine_credit = MagicMock(side_effect=get_no_credit)
        self.xblock.weight = 5
        self.xblock._compute_score()
        self.xblock.runtime.publish.assert_called_with(
            self.xblock,
            'grade',
            {'value': 0.0, 'max_value': 5}
        )

    def test_indicator_visibility_class_blank(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the get_indicator_visibility_class helper
        returns a blank class when appropriate
        """
        self.xblock.display_correctness = True
        self.assertEquals(
            '',
            self.xblock._get_indicator_visiblity_class()
        )

    def test_indicator_visibility_class_hidden(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the get_indicator_visibility_class helper
        returns 'hidden' class when appropriate
        """
        self.xblock.display_correctness = False
        self.assertEquals(
            'hidden',
            self.xblock._get_indicator_visiblity_class()
        )

    def test_determine_zero_credit_blank_answer(self):
        # pylint: disable=invalid-name, protected-access
        """
        Placeholder Docstring
        """
        self.xblock.student_answer = ''
        self.xblock._word_count_valid = MagicMock(return_value=False)
        self.assertEquals(Credit.zero, self.xblock._determine_credit())

    def test_determine_zero_credit_normal_answer(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that determine_credit() returns zero-credit when appropriate
        """
        self.xblock.student_answer = 'Non-blank answer'
        self.xblock.fullcredit_keyphrases = ['Something else']
        self.xblock.halfcredit_keyphrases = ['Something else']
        self.xblock._word_count_valid = MagicMock(return_value=True)
        self.assertEquals(Credit.zero, self.xblock._determine_credit())

    def test_determine_half_credit(self):
        # pylint: disable=protected-access
        """
        Tests that determine_credit() returns half-credit when appropriate
        """
        self.xblock.student_answer = 'Non-blank answer'
        self.xblock._word_count_valid = MagicMock(return_value=True)
        self.xblock.fullcredit_keyphrases = ['Something else']
        self.xblock.halfcredit_keyphrases = ['Non-blank', 'answer']
        self.assertEquals(Credit.half, self.xblock._determine_credit())

    def test_determine_full_credit(self):
        # pylint: disable=protected-access
        """
        Tests that determine_credit() returns full-credit when appropriate
        """
        self.xblock.student_answer = 'Non-blank answer'
        self.xblock._word_count_valid = MagicMock(return_value=True)
        self.xblock.fullcredit_keyphrases = 'Non-blank, answer'
        self.xblock.halfcredit_keyphrases = 'Something else'
        self.assertEquals(Credit.full, self.xblock._determine_credit())

    def test_used_attempts_feedback_blank(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that get_used_attempts_feedback returns no feedback when
        appropriate
        """
        self.xblock.max_attempts = 0
        self.assertEquals('', self.xblock._get_used_attempts_feedback())

    def test_used_attempts_feedback_normal(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that get_used_attempts_feedback returns the expected feedback
        """
        self.xblock.max_attempts = 5
        self.xblock.count_attempts = 3
        self.assertEquals(
            _('You have used 3 of 5 submissions'),
            self.xblock._get_used_attempts_feedback()
        )

    def test_submit_class_blank(self):
        # pylint: disable=protected-access
        """
        Tests that get_submit_class returns a blank value when appropriate
        """
        self.xblock.max_attempts = 0
        self.assertEquals('', self.xblock._get_submit_class())

    def test_submit_class_nodisplay(self):
        # pylint: disable=protected-access
        """
        Tests that get_submit_class returns the appropriate class
        when the number of attempts has exceeded the maximum number of
        permissable attempts
        """
        self.xblock.max_attempts = 5
        self.xblock.count_attempts = 6
        self.assertEquals('nodisplay', self.xblock._get_submit_class())
