from abstract_eventhandler import *
import unittest
import mock
from mock import patch, Mock
from mock import PropertyMock

class TestUpdate(unittest.TestCase):
    """
    Tests related to the abstract Event Handler
    """

    def setUp(self):

        pass

    def tearDown(self):
        pass

    # def test_main_arguments(self):
    #
    #     args = ['CRITICAL', 'SOFT', '3', 'AB-Infasa']
    #
    #     with mock.patch('abstract_eventhandler.main', return_value=None) as m:
    #         main(args)
    #
    #         #Should assert method was called
    #         self.assertTrue(m.called)

    def test_parse_state(self):
        em = EventHandler('CRITICAL', 'SOFT', '3', 'AB-Infasa', 'ignore')

        should_be_true = em.parse_state()

        self.assertTrue(should_be_true)

    def test_parse_state_false(self):
        em = EventHandler('OK', 'SOFT', '3', 'AB-Infasa', 'ignore')

        should_be_false = em.parse_state()

        self.assertFalse(should_be_false)

    def test_parse_service_attempt(self):
        em = EventHandler('OK', 'SOFT', '3', 'AB-Infasa', 'ignore')

        should_be_true = em.parse_attempt(em.handle_attempt)
        self.assertTrue(should_be_true)

        em = EventHandler('OK', 'SOFT', '5', 'AB-Infasa', 'ignore')

        should_be_true = em.parse_attempt(em.handle_attempt)
        self.assertTrue(should_be_true)

    def test_parse_service_attempt_false(self):
        em = EventHandler('OK', 'SOFT', '2', 'AB-Infasa', 'ignore')

        should_be_false = em.parse_attempt(em.handle_attempt)
        self.assertFalse(should_be_false)


    def test_parse_soft_state(self):
        #Since we are passing the default, handle on soft it's not desirable
        em = EventHandler('OK', 'SOFT', '2', 'AB-Infasa', 'ignore')


        should_be_false = em.parse_soft_attempt()
        self.assertFalse(should_be_false)

    def test_parse_soft_state_wrong_soft_attempt(self):

        #Should be false because the attempt it's below the acceptable. pss: 3
        em = EventHandler('CRITICAL', 'SOFT', '2', 'AB-Infasa', 'ignore', 'CRITICAL', 3, 3)

        should_be_false = em.parse_soft_attempt()
        self.assertFalse(should_be_false)

    def test_parse_soft_state_soft_attempt(self):

        #Should be false because the attempt it's below the acceptable. pss: 3
        em = EventHandler('CRITICAL', 'SOFT', '4', 'AB-Infasa', 'ignore', 'CRITICAL', 3, 3)

        should_be_true = em.parse_soft_attempt()
        self.assertTrue(should_be_true)

    def test_parse_soft_state_soft_attempt_wrong_state(self):

        #Should be false because the attempt it's below the acceptable. pss: 3
        em = EventHandler('WARNING', 'SOFT', '4', 'AB-Infasa', 'ignore', 'CRITICAL', 3, 3)

        should_be_false = em.parse_soft_attempt()
        self.assertFalse(should_be_false)

    def test_parse_hard_state_wrong_state(self):
        #Since we are passing the default, handle on soft it's not desirable
        em = EventHandler('OK', 'HARD', '2', 'AB-Infasa', 'ignore')


        should_be_false = em.parse_hard_attempt()
        self.assertFalse(should_be_false)

    def test_parse_hard_state_right_state_and_attempt(self):
        em = EventHandler('CRITICAL', 'HARD', '3', 'AB-Infasa', 'ignore')


        should_be_true = em.parse_hard_attempt()
        self.assertTrue(should_be_true)

    def test_parse_hard_state_right_state_and_wrong_attempt(self):
        em = EventHandler('CRITICAL', 'HARD', '2', 'AB-Infasa', 'ignore')


        should_be_false = em.parse_hard_attempt()
        self.assertFalse(should_be_false)


    def test_should_call_handler_hard_state_right_state_and_attempt(self):

        em = EventHandler('CRITICAL', 'HARD', '4', 'AB-Infasa', 'ignore')

        should_be_true = em.should_call_handler()
        self.assertTrue(should_be_true)

    def test_should_call_handler_hard_state_right_state_and_attempt_wrong_type(self):
        # This is true for HARD state but we passed soft state
        em = EventHandler('CRITICAL', 'SOFT', '4', 'AB-Infasa', 'ignore')

        should_be_false = em.should_call_handler()
        self.assertFalse(should_be_false)

    def test_should_call_handler_hard_state_right_state_and_attempt_wrong_type(self):
        # This is true for HARD state but we pass soft state
        em = EventHandler('CRITICAL', 'HARD', '4', 'AB-Infasa', 'ignore', 'CRITICAL', 3, 3)

        should_be_true = em.should_call_handler()
        self.assertTrue(should_be_true)