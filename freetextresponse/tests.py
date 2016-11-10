"""
Module Placeholder Docstring
"""
import unittest
import ddt

import mock
from django.test.client import Client
from django.utils.translation import ugettext as _
from mock import MagicMock
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xblock.field_data import DictFieldData

from .freetextresponse import Credit
from .freetextresponse import FreeTextResponse

@ddt.ddt
class FreetextResponseXblockTestCase(unittest.TestCase):
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
    A complete suite of unit tests for the Free-text Response XBlock
    """
    @classmethod
    def make_an_xblock(cls, **kw):
        """
        Helper method that creates a Free-text Response XBlock
        """
        course_id = SlashSeparatedCourseKey('foo', 'bar', 'baz')
        runtime = mock.Mock(course_id=course_id)
        scope_ids = mock.Mock()
        field_data = DictFieldData(kw)
        xblock = FreeTextResponse(runtime, field_data, scope_ids)
        xblock.xmodule_runtime = runtime
        return xblock

    def setUp(self):
        # pylint: disable=super-method-not-called
        self.xblock = FreetextResponseXblockTestCase.make_an_xblock()
        self.client = Client()

        self.xblock.fullcredit_keyphrases = []
        self.xblock.halfcredit_keyphrases = []
        self.xblock.zerocredit_keyphrases = []

        # Used for multiple tests
        self.test_fullcredit_keyphrases = [
            'list full credit phrase',
            {
                'phrase': 'first full credit dict phrase',
                'feedback': 'first full credit dict feedback'
            },
            {
                'phrase': 'second full credit dict phrase',
                'feedback': 'second full credit dict feedback'
            },
            {
             'phrase': 'lone full credit dict phrase'
            }
        ]
        self.test_halfcredit_keyphrases = [
            'list half credit phrase',
            {
                'phrase': 'first half credit dict phrase',
                'feedback': 'first half credit dict feedback'
            },
            {
                'phrase': 'second half credit dict phrase',
                'feedback': 'second half credit dict feedback'
            },
            {
             'phrase': 'lone half credit dict phrase'
            }
        ]
        self.test_zerocredit_keyphrases = [
            'list zero credit phrase',
            {
                'phrase': 'first zero credit dict phrase',
                'feedback': 'first zero credit dict feedback'
            },
            {
                'phrase': 'second zero credit dict phrase',
                'feedback': 'second zero credit dict feedback'
            },
            {
             'phrase': 'lone zero credit dict phrase'
            }
        ]

    def student_view_html(self):
        """
        Helper method that returns the html of student_view
        """
        return self.xblock.student_view().content

    def test_student_view(self):
        # pylint: disable=protected-access
        """
        Checks the student view for student specific instance variables.
        """
        student_view_html = self.student_view_html()
        self.assertIn(self.xblock.display_name, student_view_html)
        self.assertIn(self.xblock.prompt, student_view_html)
        # Messages
        self.assertIn(self.xblock._get_problem_progress(), student_view_html)
        self.assertIn(self.xblock._get_used_attempts_feedback(), student_view_html)
        # CSS Classes
        self.assertIn(self.xblock._get_indicator_class(), student_view_html)
        self.assertIn(self.xblock._get_indicator_visibility_class(), student_view_html)
        self.assertIn(self.xblock._get_submitdisplay_class(), student_view_html)
        self.assertIn(self.xblock._get_hintdisplay_class(), student_view_html)

    def studio_view_html(self):
        """
        Helper method that returns the html of studio_view
        """
        return self.xblock.studio_view(context=None).content

    def test_studio_view(self):
        """
        Checks studio view for instance variables specified by the instructor.
        """
        studio_view_html = self.studio_view_html()
        self.assertIn(self.xblock.display_name, studio_view_html)
        self.assertIn(self.xblock.prompt, studio_view_html)
        self.assertIn(str(self.xblock.max_attempts), studio_view_html)
        self.assertIn(str(self.xblock.weight), studio_view_html)
        self.assertIn(
            ', '.join(
                self.xblock.fullcredit_keyphrases,
            ),
            studio_view_html,
        )
        self.assertIn(
            ', '.join(
                self.xblock.halfcredit_keyphrases,
            ),
            studio_view_html,
        )
        self.assertIn(
            ', '.join(
                self.xblock.zerocredit_keyphrases,
            ),
            studio_view_html,
        )
        self.assertIn(str(self.xblock.display_correctness), studio_view_html)
        self.assertIn(str(self.xblock.min_word_count), studio_view_html)
        self.assertIn(str(self.xblock.max_word_count), studio_view_html)
        self.assertIn(str(self.xblock.submitted_message), studio_view_html)

    def test_initialization_variables(self):
        """
        Checks that all instance variables are initialized correctly
        """
        self.assertEquals('Free-text Response', self.xblock.display_name)
        self.assertEquals(
            'Please enter your response within this text area',
            self.xblock.prompt,
        )
        self.assertEquals(0, self.xblock.max_attempts)
        self.assertEquals(0, self.xblock.weight)
        self.assertEquals(
            [],
            self.xblock.fullcredit_keyphrases,
        )
        self.assertEquals(
            [],
            self.xblock.halfcredit_keyphrases,
        )
        self.assertEquals(
            [],
            self.xblock.zerocredit_keyphrases,
        )
        self.assertTrue(self.xblock.display_correctness)
        self.assertEquals(1, self.xblock.min_word_count)
        self.assertEquals(10000, self.xblock.max_word_count)
        self.assertEquals([], self.xblock.hints)
        self.assertEquals(
            'Your submission has been received',
            self.xblock.submitted_message
        )
        self.assertEquals(0, self.xblock.count_attempts)
        self.assertEquals(0.0, self.xblock.score)
        self.assertEquals('', self.xblock.student_answer)
        self.assertEquals(0, self.xblock.hint_counter)

    # Scoring
    @ddt.data(Credit.zero, Credit.half, Credit.full)
    def test_compute_score(self, credit):
        # pylint: disable=protected-access
        """
        Tests that a credit grade is assigned when appropriate
        """
        self.xblock.runtime.publish = MagicMock(return_value=None)
        self.xblock._determine_credit = MagicMock(return_value=credit)
        self.xblock._compute_score()
        self.xblock.runtime.publish.assert_called_with(
            self.xblock,
            'grade',
            {'value': credit.value, 'max_value': Credit.full.value},
        )

    def test_get_phrases(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests the _get_phrases class method with
        the fullcredit_keyphrases list dict and a
        list of the fullcredit_keyphrases phrases
        """
        keyphrases_list = [
            'list full credit phrase',
            'first full credit dict phrase',
            'second full credit dict phrase',
            'lone full credit dict phrase'
        ]
        self.assertItemsEqual(
            keyphrases_list,
            FreeTextResponse._get_phrases(self.test_fullcredit_keyphrases)
        )

    def test_is_at_least_one_phrase_present(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests the _is_at_least_one_phrase_present helper method
        """
        keyphrases_list = [
            'do dict phrase',
            're dict phrase',
            'mi dict phrase',
            'fa dict phrase'
        ]
        answer = keyphrases_list[1]
        ansert = 'ajhsdfhjaefhaf ' + answer + 'jkfbaufebn;  fuqv'
        self.assertTrue(
            FreeTextResponse._is_at_least_one_phrase_present(
                keyphrases_list,
                answer,
            ),
        )

    def test_not_is_at_least_one_phrase_present(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests the _is_at_least_one_phrase_present helper method
        """
        keyphrases_list = [
            'do dict phrase',
            're dict phrase',
            'mi dict phrase',
            'fa dict phrase'
        ]
        answer = 'so dict phrase'
        ansert = 'ajhsdfhjaefhaf ' + answer + 'jkfbaufebn;  fuqv'
        self.assertFalse(
            FreeTextResponse._is_at_least_one_phrase_present(
                keyphrases_list,
                answer,
            ),
        )

    @ddt.data(
        ('any thing will do', Credit.full),
        ('', Credit.zero),
    )
    @ddt.unpack
    def test_determine_credit_empty_keyphrases(self, student_answer, credit):
        # pylint: disable=protected-access
        """
        Tests determine_credit() with full-credit phrases
        -Full credit takes precedence over half and zero credit
        """
        self.xblock.student_answer = student_answer
        self.xblock.fullcredit_keyphrases = []
        self.xblock.halfcredit_keyphrases = []
        self.xblock.zerocredit_keyphrases = []
        self.assertEquals(credit, self.xblock._determine_credit())

    @ddt.data(
        # Full
        ('list full credit phrase', Credit.full),
        ('second full credit dict phrase', Credit.full),
        ('lone full credit dict phrase', Credit.full),
        # half
        ('list half credit phrase', Credit.half),
        ('second half credit dict phrase', Credit.half),
        ('lone half credit dict phrase', Credit.half),
        # zero
        ('list zero credit phrase', Credit.zero),
        ('second zero credit dict phrase', Credit.zero),
        ('lone zero credit dict phrase', Credit.zero),
    )
    @ddt.unpack
    def test_determine_credit(self, student_answer, credit):
        # pylint: disable=protected-access
        """
        Tests determine_credit() with full-credit phrases
        -Full credit takes precedence over half and zero credit
        """
        self.xblock.student_answer = student_answer
        self.xblock.fullcredit_keyphrases = self.test_fullcredit_keyphrases
        self.xblock.halfcredit_keyphrases = self.test_halfcredit_keyphrases
        self.xblock.zerocredit_keyphrases = self.test_zerocredit_keyphrases
        self.assertEquals(credit, self.xblock._determine_credit())

    @ddt.data(
        # min_word_count, max_word_count, student_answer, result
        (1, 2, '', False),                              # Answer Blank
        (1, 2, 'One', True),                            # Answer Equals Min
        (1, 2, 'One Two', True),                        # Answer Equals Max
        (2, 4, 'One Two Three Four Five', False),       # Answer Too Long
        (2, 4, 'One', False),                           # Answer Too Short
        (3, 6, 'One Two Three Four Five', True),        # Answer In Range
    )
    @ddt.unpack
    def test_word_count_valid(self, min_word_count, max_word_count, student_answer, result):
        # pylint: disable=protected-access
        """
        Tests _word_count_valid
        """
        self.xblock.min_word_count = min_word_count
        self.xblock.max_word_count = max_word_count
        self.xblock.student_answer = student_answer
        self.assertEquals(result, self.xblock._word_count_valid())

    #Messages
    @ddt.data(
        # weight, score, result
        (0, 0, ''),
        # Singluar Weight
        (1, 0, '(1 point possible)'),
        (1, 1, '(1/1 point)'),
        # Plural Weight
        # Small Number
        (5, 0, '(5 points possible)'),
        (5, 0.5, '(2.5/5 points)'),
        (5, 1, '(5/5 points)'),
        # Large Even Number
        (975312468, 0, '(975312468 points possible)'),
        (975312468, 0.5, '(487656234/975312468 points)'),
        (975312468, 1, '(975312468/975312468 points)'),
        # Large Odd Number at half credit
        (7919, 0.5, '(3959.5/7919 points)'),
    )
    @ddt.unpack
    def test_get_problem_progress(self, weight, score, result):
        # pylint: disable=invalid-name, protected-access
        """
        Tests _get_problem_progress
        Score can be 0, 0.5, or 1
        """
        self.xblock.weight = weight
        self.xblock.score = score
        self.assertEquals(
            _(result),
            self.xblock._get_problem_progress(),
        )

    @ddt.data(
        # max_attempts, count_attempts, result
        (0, 4, ''),
        (1, 0, 'You have used 0 of 1 submission'),
        (3, 2, 'You have used 2 of 3 submissions'),
    )
    @ddt.unpack
    def test_used_attempts_feedback_normal(
        self,
        max_attempts,
        count_attempts,
        result
    ):
        # pylint: disable=invalid-name, protected-access
        """
        Tests get_used_attempts_feedback
        """
        self.xblock.max_attempts = max_attempts
        self.xblock.count_attempts = count_attempts
        self.assertEquals(
            _(result),
            self.xblock._get_used_attempts_feedback(),
        )

    @ddt.data(
        # word_count_valid, feedback_text, result
        (False, None, ''),
        (True, 'Answer Feedback', ''),
        (True, None, 'test submission received message'),
        (True, '', 'test submission received message'),
    )
    @ddt.unpack
    def test_get_submitted_message(self, word_count_valid, feedback_text, result):
        # pylint: disable=invalid-name, protected-access
        """
        Tests _get_submitted_message
        """
        self.xblock._word_count_valid = MagicMock(return_value=word_count_valid)
        self.xblock.submitted_message = 'test submission received message'
        self.assertEquals(
            _(result),
            self.xblock._get_submitted_message(feedback_text),
        )

    @ddt.data(
        # student_answer, result
        ('not an option', None),
        ('list full credit phrase', None),
        ('second full credit dict phrase', 'second full credit dict feedback'),
        ('lone full credit dict phrase', None),
    )
    @ddt.unpack
    def test_get_feedback_if_phrase_present(
        self,
        student_answer,
        result
    ):
        # pylint: disable=invalid-name, protected-access
        """
        Tests _get_feedback_if_phrase_present
        """
        self.assertEquals(
            result,
            FreeTextResponse._get_feedback_if_phrase_present(
                self.test_fullcredit_keyphrases,
                student_answer,
            ),
        )

    @ddt.data(
        # student_answer, credit_score, label_result, feedback_result, keyphrases
        (
            'second full credit dict phrase',
            Credit.full.value,
            'Correct:',
            'second full credit dict feedback',
        ),
        (
            'first half credit dict phrase',
            Credit.half.value,
            'Correct:',
            'first half credit dict feedback',
        ),
        (
            'second zero credit dict phrase',
            Credit.zero.value,
            'Incorrect:',
            'second zero credit dict feedback',
        ),
        (
            'list full credit phrase',
            Credit.full.value,
            '',
            '',
        ),
        (
            'lone zero credit dict phrase',
            Credit.zero.value,
            '',
            '',
        ),
    )
    @ddt.unpack
    def test_get_feedback(
        self,
        student_answer,
        credit_score,
        label_result,
        feedback_result,
    ):
        # pylint: disable=invalid-name, protected-access
        """
        Tests _get_feedback_if_phrase_present
        """
        self.xblock.score = credit_score
        self.xblock.student_answer = student_answer
        self.xblock.zerocredit_keyphrases = self.test_zerocredit_keyphrases
        self.xblock.halfcredit_keyphrases = self.test_halfcredit_keyphrases
        self.xblock.fullcredit_keyphrases = self.test_fullcredit_keyphrases
        #original_cls_fn = FreeTextResponse._get_feedback_if_phrase_present
        #self.xblock._get_feedback_if_phrase_present = MagicMock(return_value=feedback_result)
        (feedback_label, feedback_text) = self.xblock._get_feedback()
        # Label
        self.assertEquals(label_result, feedback_label)
        # Feedback
        self.assertEquals(feedback_result, feedback_text)
        #FreeTextResponse._get_feedback_if_phrase_present = original_cls_fn

    # Get Hint text
    @ddt.data(
        # hints, hint_counter, result
        # unanswered cases
        ([], 0, ''),
        (['h1', 'h2', 'h3', 'h4', 'h5'], 0, 'Hint (1 of 5):h1'),
        (['h1', 'h2', 'h3', 'h4'], 3, 'Hint (4 of 4):h4'),
        (['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7'], 8, 'Hint (2 of 7):h2'),
    )
    @ddt.unpack
    def test_get_hint_text(
        self,
        hints,
        hint_counter,
        result,
    ):
        # disable=invalid-name, protected-access
        """
        Test _get_hint_text
        """
        print hints
        self.xblock.hints = hints
        self.xblock.hint_counter = hint_counter
        self.assertEquals(result, self.xblock._get_hint_text())

    @ddt.data(
        # word_count_valid, count_attempts, min_word_count, max_word_count, ignore_attempts, result
        # EMPTY RESULTS
        # Valid word count, No count attempts
        (True, 0, 1, 10000, False, ''),
        # Valid word count, Count attempts
        (True, 1, 1, 10000, False, ''),
        # Valid word count, Ignore Count attempts
        (True, 0, 1, 10000, True, ''),
        # Invalid word count, No count attempts
        (False, 0, 1, 10000, False, ''),
        # SINGULAR RESULT => invalid word count
        # -Impossible becuase max_word_count must be
        # greater than min_word_count, which has a min of 1
        (False, 1, 1, 1, False, None),
        # PLURAL RESULT => invalid word count
        (False, 1, 4, 10000, False, None),
    )
    @ddt.unpack
    def test_get_user_alert(
        self,
        word_count_valid,
        count_attempts,
        min_word_count,
        max_word_count,
        ignore_attempts,
        result,
    ):
        # pylint: disable=invalid-name, protected-access
        """
        Tests _get_user_alert
        count_attempts  default: 0
        max_word_count  default: 10000   min: 1
        min_word_count  default: 1       min: 1
        """
        self.xblock._word_count_valid = MagicMock(return_value=word_count_valid)
        self.xblock.count_attempts = count_attempts
        self.xblock.min_word_count = min_word_count
        self.xblock.max_word_count = max_word_count
        if None == result:
            result = 'Invalid Word Count. Your response must be ' \
                'between ' + str(min_word_count) + ' and ' + str(max_word_count)
            if 1 >= max_word_count:
                result += ' word.'
            else:
                result += ' words.'
        self.assertEquals(
            _(result),
            self.xblock._get_user_alert(ignore_attempts=ignore_attempts),
        )

    @ddt.data(
        # word_count_valid, count_attempts, min_word_count, max_word_count, ignore_attempts, result
        # EMPTY RESULTS
        # Valid word count, No count attempts
        (True, 0, 1, 10000, False, ''),
        # Valid word count, Count attempts
        (True, 1, 1, 10000, False, ''),
        # Valid word count, Ignore Count attempts
        (True, 0, 1, 10000, True, ''),
        # Invalid word count, No count attempts
        (False, 0, 1, 10000, False, ''),
        # SINGULAR RESULT => invalid word count
        # -Impossible becuase max_word_count must be
        # greater than min_word_count, which has a min of 1
        (False, 1, 1, 1, False, None),
        # PLURAL RESULT => invalid word count
        (False, 1, 4, 10000, False, None),
    )
    @ddt.unpack
    def test_get_word_count_message(
        self,
        word_count_valid,
        count_attempts,
        min_word_count,
        max_word_count,
        ignore_attempts,
        result,
    ):
        # pylint: disable=invalid-name, protected-access
        """
        Tests _get_word_count_message
        count_attempts  default: 0
        max_word_count  default: 10000   min: 1
        min_word_count  default: 1       min: 1
        """
        self.xblock._word_count_valid = MagicMock(return_value=word_count_valid)
        self.xblock.count_attempts = count_attempts
        self.xblock.min_word_count = min_word_count
        self.xblock.max_word_count = max_word_count
        if None == result:
            result = 'Invalid Word Count. Your response must be ' \
                'between ' + str(min_word_count) + ' and ' + str(max_word_count)
            if 1 >= max_word_count:
                result += ' word.'
            else:
                result += ' words.'
        self.assertEquals(
            _(result),
            self.xblock._get_word_count_message(ignore_attempts=ignore_attempts),
        )

    # CSS Classes
    @ddt.data(
        # display_correctness, word_count_valid, credit, result
        # unanswered cases
        (True, False, None, 'unanswered'),
        (False, True, None, 'unanswered'),
        # incorrect cases
        (True, True, Credit.zero, 'incorrect'),
        # correct cases
        (True, True, Credit.full, 'correct'),
        (True, True, Credit.half, 'correct'),
    )
    @ddt.unpack
    def test_get_indicator_class(
        self,
        display_correctness,
        word_count_valid,
        credit,
        result
    ):
        # disable=invalid-name, protected-access
        """
        Test _get_indicator_class
        """
        self.xblock.display_correctness = display_correctness
        self.xblock._word_count_valid = MagicMock(return_value=word_count_valid)
        self.xblock._determine_credit = MagicMock(return_value=credit)
        self.assertEquals(result, self.xblock._get_indicator_class())

    @ddt.data(
        # display_correctness, result
        (True, ''),
        (False, 'hidden'),
    )
    @ddt.unpack
    def test_get_indicator_visibility_class(self, display_correctness, result):
        # pylint: disable=invalid-name, protected-access
        """
        Tests _get_indicator_visibility_class
        """
        self.xblock.display_correctness = display_correctness
        self.assertEquals(
            result,
            self.xblock._get_indicator_visibility_class(),
        )

    @ddt.data(
        # max_attempts, count_attempts, result
        # empty results
        (0, 1, ''),
        (3, 2, ''),
        # 'nodisplay' results
        (3, 3, 'nodisplay'),
        (3, 4, 'nodisplay'),
    )
    @ddt.unpack
    def test_get_submitdisplay_class(self, max_attempts, count_attempts, result):
        # pylint: disable=protected-access
        """
        Tests _get_submitdisplay_class
        """
        self.xblock.max_attempts = max_attempts
        self.xblock.count_attempts = count_attempts
        self.assertEquals(result, self.xblock._get_submitdisplay_class())

    @ddt.data(
        # hints, result
        (['hint 1', 'hint 2'], ''),
        ([], 'nodisplay'),
    )
    @ddt.unpack
    def test_get_hintdisplay_class(self, hints, result):
        # pylint: disable=protected-access
        """
        Tests _get_hintdisplay_class
        """
        self.xblock.hints = hints
        self.assertEquals(result, self.xblock._get_hintdisplay_class())

    # Default View
    # Handlers to perform actions
