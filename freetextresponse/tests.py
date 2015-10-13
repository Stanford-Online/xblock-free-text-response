'''
Module Placeholder Docstring
'''
import unittest

import mock
from mock import MagicMock
from django.test.client import Client
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xblock.field_data import DictFieldData
from .freetextresponse import Freetextresponse
from .freetextresponse import Credit


class FreetextResponseXblockTests(unittest.TestCase):
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    '''
    A complete suite of unit tests for the FreeTextXBlock
    '''
    @classmethod
    def make_an_xblock(cls, **kw):
        '''
        Helper method that creates a FreeTextResponse XBlock
        '''
        course_id = SlashSeparatedCourseKey('foo', 'bar', 'baz')
        runtime = mock.Mock(course_id=course_id)
        scope_ids = mock.Mock()

        field_data = DictFieldData(kw)
        xblock = Freetextresponse(runtime, field_data, scope_ids)
        xblock.xmodule_runtime = runtime
        return xblock

    def setUp(self):
        self.xblock = FreetextResponseXblockTests.make_an_xblock()
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
        self.test_num_attempts = '3'

    def test_student_view(self):
        '''
        Checks the student view for student specific instance variables.
        '''
        student_view_html = self.student_view_html()
        self.assertIn(self.xblock.display_name, student_view_html)
        self.assertIn(self.xblock.prompt, student_view_html)
        self.assertIn(self.xblock.get_indicator_class(), student_view_html)
        self.assertIn(self.xblock.get_problem_progress(), student_view_html)

    def test_studio_view(self):
        '''
        Checks studio view for instance variables specified by the instructor.
        '''
        studio_view_html = self.studio_view_html()
        self.assertIn(self.xblock.display_name, studio_view_html)
        self.assertIn(self.xblock.prompt, studio_view_html)
        self.assertIn(str(self.xblock.max_attempts), studio_view_html)
        self.assertIn(self.xblock.display_correctness, studio_view_html)
        self.assertIn(str(self.xblock.min_word_count), studio_view_html)
        self.assertIn(str(self.xblock.max_word_count), studio_view_html)
        self.assertIn(self.xblock.fullcredit_keyphrases, studio_view_html)
        self.assertIn(self.xblock.halfcredit_keyphrases, studio_view_html)

    def test_initialization_variables(self):
        '''
        Checks that all instance variables are initialized correctly
        '''
        self.assertEquals('FreeText XBlock', self.xblock.display_name)
        self.assertEquals(
            'Please enter your response within this text area',
            self.xblock.prompt
        )
        self.assertEquals(0.0, self.xblock.score)
        self.assertEquals(0, self.xblock.max_attempts)
        self.assertEquals('True', self.xblock.display_correctness)
        self.assertEquals(0, self.xblock.min_word_count)
        self.assertEquals(10000, self.xblock.max_word_count)
        self.assertEquals(
            'Full-Credit Phrase 1, '
            'Full-Credit Phrase 2, '
            'Full-Credit Phrase 3',
            self.xblock.fullcredit_keyphrases
        )
        self.assertEquals(
            'Half-Credit Phrase 1, '
            'Half-Credit Phrase 2, '
            'Half-Credit Phrase 3',
            self.xblock.halfcredit_keyphrases
        )
        self.assertEquals('', self.xblock.student_answer)
        self.assertEquals(0, self.xblock.num_attempts)

    def student_view_html(self):
        '''
        Helper method that returns the html of student_view
        '''
        return self.xblock.student_view().content

    def studio_view_html(self):
        '''
        Helper method that returns the html of studio_view
        '''
        return self.xblock.studio_view().content

    def test_studio_view_save(self):
        '''
        Tests that the XBlock properly saves data  that is changed by the
        instructor
        '''
        data = {}
        data['display_name'] = self.test_display_name
        data['prompt'] = self.test_prompt
        data['weight'] = self.test_weight
        data['max_attempts'] = self.test_max_attempts
        data['display_correctness'] = self.test_display_correctness
        data['min_word_count'] = self.test_min_word_count
        data['max_word_count'] = self.test_max_word_count
        data['fullcredit_keyphrases'] = self.test_fullcredit_keyphrases
        data['halfcredit_keyphrases'] = self.test_halfcredit_keyphrases

        response = self.xblock.save_studio_data(data)

        self.assertEquals(self.test_display_name, response.get('display_name'))
        self.assertEquals(self.test_prompt, response.get('prompt'))
        self.assertEquals(self.test_weight, response.get('weight'))
        self.assertEquals(self.test_max_attempts, response.get('max_attempts'))
        self.assertEquals(
            self.test_display_correctness,
            response.get('display_correctness')
        )
        self.assertEquals(
            self.test_min_word_count,
            response.get('min_word_count')
        )
        self.assertEquals(
            self.test_max_word_count,
            response.get('max_word_count')
        )
        self.assertEquals(
            self.test_fullcredit_keyphrases,
            response.get('fullcredit_keyphrases')
        )
        self.assertEquals(
            self.test_halfcredit_keyphrases,
            response.get('halfcredit_keyphrases')
        )

    def test_word_count_message_blank_when_attempts_0(self):
        # pylint: disable=invalid-name
        '''
        Tests that the word count message is blank when the
        user has made zero attempts
        '''
        self.xblock.num_attempts = 0
        self.assertEquals('', self.xblock.get_word_count_message())

    def test_word_count_message_blank_when_word_count_valid(self):
        # pylint: disable=invalid-name
        '''
        Tests that the word count message doesn't display when
        the word count is valid
        '''
        self.xblock.num_attempts = 5
        self.xblock.word_count_valid = MagicMock(return_value=True)
        self.assertEquals('', self.xblock.get_word_count_message())

    def test_invalid_word_count_message(self):
        '''
        Tests that the invalid word count message displays
        when appropriate
        '''
        self.xblock.num_attempts = 5
        self.xblock.word_count_valid = MagicMock(return_value=False)
        self.assertIn(
            'Invalid Word Count. Your reponse must be between',
            self.xblock.get_word_count_message()
        )

    def test_indicator_class_unanswered(self):
        '''
        Tests that the 'unanswered' class for the display_correctness
        html component displays when appropriate
        '''
        self.xblock.student_answer = ''
        self.xblock.num_attempts = 0
        self.assertEquals('unanswered', self.xblock.get_indicator_class())

    def test_indicator_class_incorrect_blank_response(self):
        # pylint: disable=invalid-name
        '''
        Tests that the 'incorrect' class for the display_correctness html
        component displays when the response is blank
        '''
        self.xblock.student_answer = ''
        self.xblock.num_attempts = 5
        self.assertEquals('incorrect', self.xblock.get_indicator_class())

    def test_indicator_class_incorrect_normal_response(self):
        # pylint: disable=invalid-name
        '''
        Tests that the 'incorrect' class for the display_correctness
        html component displays when the response is incorrect
        '''
        self.xblock.student_answer = 'Non-blank response'
        self.xblock.num_attempts = 5
        self.xblock.word_count_valid = MagicMock(return_value=False)
        self.xblock.phrase_present_in_answer = MagicMock(return_value=False)
        self.assertEquals('incorrect', self.xblock.get_indicator_class())

    def test_indicator_class_correct_normal_response(self):
        # pylint: disable=invalid-name
        '''
        Tests that the 'correct' class for the display_correctness html
        component displays when the response is correct
        '''
        self.xblock.student_answer = 'Non-blank response'
        self.xblock.num_attempts = 5
        self.xblock.word_count_valid = MagicMock(return_value=True)
        self.xblock.phrase_present_in_answer = MagicMock(return_value=True)
        self.assertEquals('correct', self.xblock.get_indicator_class())

    def test_word_count_in_range(self):
        '''
        Tests that the word_count_valid method returns the
        appropriate response when the word count is valid
        '''
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 1
        self.xblock.max_word_count = 5
        self.assertTrue(self.xblock.word_count_valid())

    def test_word_count_min(self):
        '''
        Tests that the word_count_valid method returns the
        appropriate response when the student's answer has
        the minimum number of permissible words
        '''
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 3
        self.xblock.max_word_count = 5
        self.assertTrue(self.xblock.word_count_valid())

    def test_word_count_max(self):
        '''
        Tests that the word_count_valid method returns the
        appropriate response when the student's answer has
        the maximum number of permissible words
        '''
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 0
        self.xblock.max_word_count = 3
        self.assertTrue(self.xblock.word_count_valid())

    def test_word_count_too_short(self):
        '''
        Tests that the word_count_valid method returns the
        appropriate response when the student's answer
        is too short
        '''
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 4
        self.xblock.max_word_count = 5
        self.assertFalse(self.xblock.word_count_valid())

    def test_word_count_too_long(self):
        '''
        Tests that the word_count_valid method returns the
        appropriate response when the student's answer
        is too long
        '''
        self.xblock.student_answer = 'One two three'
        self.xblock.min_word_count = 0
        self.xblock.max_word_count = 2
        self.assertFalse(self.xblock.word_count_valid())

    def test_phrase_present_in_answer(self):
        # pylint: disable=invalid-name
        '''
        Tests the phrase_present_in_answer helper method, when at least
        of of the phrases is present in the answer
        '''
        pattern_list = "Battle Ends, And, Down, Goes  , Charles' Father"
        self.xblock.student_answer = "cHarleS' fAther went to the store to " \
                                     "buy honey"
        self.assertTrue(self.xblock.phrase_present_in_answer(pattern_list))

    def test_pattern_not_present_in_answer(self):
        # pylint: disable=invalid-name
        '''
        Tests the phrase_present_in_answer helper method, when none of the
        phrases are present in the anaswer
        '''
        pattern_list = "Battle Ends, And, Down, Goes  , Charles' Father"
        self.xblock.student_answer = "cHarleS' mother went to the store to " \
                                     "buy honey"
        self.assertFalse(self.xblock.phrase_present_in_answer(pattern_list))

    def test_problem_progress_score_zero_weight_singular(self):
        # pylint: disable=invalid-name
        '''
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is singular, and the score is zero
        '''
        self.xblock.score = 0
        self.xblock.weight = 1
        self.assertEquals(
            '1 point possible',
            self.xblock.get_problem_progress()
        )

    def test_problem_progress_score_zero_weight_plural(self):
        # pylint: disable=invalid-name
        '''
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is plural, and the score is zero
        '''
        self.xblock.score = 0
        self.xblock.weight = 3
        self.assertEquals(
            '3 points possible',
            self.xblock.get_problem_progress()
        )

    def test_problem_progress_score_positive_weight_singular(self):
        # pylint: disable=invalid-name
        '''
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is singular, and the score is positive
        '''
        self.xblock.score = 1
        self.xblock.weight = 1
        self.assertEquals('1/1 point', self.xblock.get_problem_progress())

    def test_problem_progress_score_positive_weight_plural(self):
        # pylint: disable=invalid-name
        '''
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is plural, and the score is positive
        '''
        self.xblock.score = 1.5
        self.xblock.weight = 3
        self.assertEquals('1.5/3 points', self.xblock.get_problem_progress())

    def test_compute_score_full_credit(self):
        '''
        Tests that a full-credit grade is assigned when appropriate
        '''
        def get_full_credit():
            '''
            Side-effect that returns full credit
            '''
            return Credit.full
        self.xblock.runtime.publish = MagicMock(return_value=None)
        self.xblock.determine_credit = MagicMock(side_effect=get_full_credit)
        self.xblock.weight = 5
        self.xblock.compute_score()
        self.xblock.runtime.publish.assert_called_with(
            self.xblock,
            "grade",
            {'value': 5.0, 'max_value': 5}
        )

    def test_compute_score_half_credit(self):
        '''
        Tests that a half-credit grade is assigned when appropriate
        '''
        def get_half_credit():
            '''
            Side-effect that returns half credit
            '''
            return Credit.half
        self.xblock.runtime.publish = MagicMock(return_value=None)
        self.xblock.determine_credit = MagicMock(side_effect=get_half_credit)
        self.xblock.weight = 5
        self.xblock.compute_score()
        self.xblock.runtime.publish.assert_called_with(
            self.xblock,
            "grade",
            {'value': 2.5, 'max_value': 5}
        )

    def test_compute_score_no_credit(self):
        '''
        Tests that a no-credit grade is assigned when appropriate
        '''
        def get_no_credit():
            '''
            Side-effect that returns no credit
            '''
            return Credit.zero
        self.xblock.runtime.publish = MagicMock(return_value=None)
        self.xblock.determine_credit = MagicMock(side_effect=get_no_credit)
        self.xblock.weight = 5
        self.xblock.compute_score()
        self.xblock.runtime.publish.assert_called_with(
            self.xblock,
            "grade",
            {'value': 0.0, 'max_value': 5}
        )

    def test_indicator_visibility_class_blank(self):
        # pylint: disable=invalid-name
        '''
        Tests that the get_indicator_visibility_class helper
        returns a blank class when appropriate
        '''
        self.xblock.display_correctness = 'true'
        self.assertEquals(
            '',
            self.xblock.get_indicator_visiblity_class()
        )

    def test_indicator_visibility_class_hidden(self):
        # pylint: disable=invalid-name
        '''
        Tests that the get_indicator_visibility_class helper
        returns 'hidden' class when appropriate
        '''
        self.xblock.display_correctness = 'fALse'
        self.assertEquals(
            'hidden',
            self.xblock.get_indicator_visiblity_class()
        )

    def test_determine_zero_credit_blank_answer(self):
        # pylint: disable=invalid-name
        '''
        Placeholder Docstring
        '''
        self.xblock.student_answer = ''
        self.xblock.word_count_valid = MagicMock(return_value=False)
        self.assertEquals(Credit.zero, self.xblock.determine_credit())

    def test_determine_zero_credit_normal_answer(self):
        # pylint: disable=invalid-name
        '''
        Tests that determine_credit() returns zero-credit when appropriate
        '''
        self.xblock.student_answer = 'Non-blank answer'
        self.xblock.fullcredit_keyphrases = 'Something else'
        self.xblock.halfcredit_keyphrases = 'Something else'
        self.xblock.word_count_valid = MagicMock(return_value=True)
        self.assertEquals(Credit.zero, self.xblock.determine_credit())

    def test_determine_half_credit(self):
        '''
        Tests that determine_credit() returns half-credit when appropriate
        '''
        self.xblock.student_answer = 'Non-blank answer'
        self.xblock.word_count_valid = MagicMock(return_value=True)
        self.xblock.fullcredit_keyphrases = 'Something else'
        self.xblock.halfcredit_keyphrases = 'Non-blank, answer'
        self.assertEquals(Credit.half, self.xblock.determine_credit())

    def test_determine_full_credit(self):
        '''
        Tests that determine_credit() returns full-credit when appropriate
        '''
        self.xblock.student_answer = 'Non-blank answer'
        self.xblock.word_count_valid = MagicMock(return_value=True)
        self.xblock.fullcredit_keyphrases = 'Non-blank, answer'
        self.xblock.halfcredit_keyphrases = 'Something else'
        self.assertEquals(Credit.full, self.xblock.determine_credit())

    def test_used_attempts_feedback_blank(self):
        # pylint: disable=invalid-name
        '''
        Tests that get_used_attempts_feedback returns no feedback when
        appropriate
        '''
        self.xblock.max_attempts = 0
        self.assertEquals('', self.xblock.get_used_attempts_feedback())

    def test_used_attempts_feedback_normal(self):
        # pylint: disable=invalid-name
        '''
        Tests that get_used_attempts_feedback returns the expected feedback
        '''
        self.xblock.max_attempts = 5
        self.xblock.num_attempts = 3
        self.assertEquals(
            'You have used 3 of 5 submissions',
            self.xblock.get_used_attempts_feedback()
        )

    def test_submit_class_blank(self):
        '''
        Tests that get_submit_class returns a blank value when appropriate
        '''
        self.xblock.max_attempts = 0
        self.assertEquals('', self.xblock.get_submit_class())

    def test_submit_class_nodisplay(self):
        '''
        Tests that get_submit_class returns the appropriate class
        when the number of attempts has exceeded the maximum number of
        permissable attempts
        '''
        self.xblock.max_attempts = 5
        self.xblock.num_attempts = 6
        self.assertEquals('nodisplay', self.xblock.get_submit_class())
