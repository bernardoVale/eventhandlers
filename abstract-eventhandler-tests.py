from abstract_eventhandler import *
import unittest
import mock
from mock import patch, Mock
from mock import PropertyMock

class TestEventHandlerBuild(unittest.TestCase):

    """
    Tests related to the building of anEvent Handler
    """

    def setUp(self):

        pass

    def tearDown(self):
        pass

    def test_non_optional_arguments(self):
        args = ['CRITICAL', 'SOFT', '3', 'AB-Infasa', 'ignore']
        expected = EventHandler('CRITICAL', 'SOFT', '3', 'AB-Infasa', 'ignore')
        got = parse_args(args)

        self.assertEqual(expected.service_state, got.service_state)
        self.assertEqual(expected.service_state_type, got.service_state_type)
        self.assertEqual(expected.service_attempt, got.service_attempt)
        self.assertEqual(expected.hostname, got.hostname)
        self.assertEqual(expected.handler_name, got.handler_name)

    def test_optionals_arguments_handler_state(self):
        args = ['CRITICAL', 'SOFT', '3', 'AB-Infasa', 'ignore', 'WARNING']
        expected = EventHandler('CRITICAL', 'SOFT', '3', 'AB-Infasa', 'ignore','WARNING')
        got = parse_args(args)

        self.assertEqual(expected.service_state, got.service_state)
        self.assertEqual(expected.service_state_type, got.service_state_type)
        self.assertEqual(expected.service_attempt, got.service_attempt)
        self.assertEqual(expected.hostname, got.hostname)
        self.assertEqual(expected.handler_name, got.handler_name)
        self.assertEqual(expected.handle_state, got.handle_state)

    def test_optionals_arguments_handle_on_soft_attempt(self):
        args = ['CRITICAL', 'SOFT', '3', 'AB-Infasa', 'ignore', 'WARNING', '4']
        expected = EventHandler('CRITICAL', 'SOFT', '3', 'AB-Infasa', 'ignore','WARNING', '4')
        got = parse_args(args)

        self.assertEqual(expected.service_state, got.service_state)
        self.assertEqual(expected.service_state_type, got.service_state_type)
        self.assertEqual(expected.service_attempt, got.service_attempt)
        self.assertEqual(expected.hostname, got.hostname)
        self.assertEqual(expected.handler_name, got.handler_name)
        self.assertEqual(expected.handle_state, got.handle_state)
        self.assertEqual(expected.handle_on_soft_attempt, got.handle_on_soft_attempt)

class TestParse(unittest.TestCase):
    """
    Tests related to parsing the Event Handler
    """

    def setUp(self):

        pass

    def tearDown(self):
        pass

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

        should_be_true = em.parse_attempt(3)
        self.assertTrue(should_be_true)

        em = EventHandler('OK', 'SOFT', '5', 'AB-Infasa', 'ignore')

        should_be_true = em.parse_attempt(3)
        self.assertTrue(should_be_true)

    def test_parse_service_attempt_false(self):
        em = EventHandler('OK', 'SOFT', '4', 'AB-Infasa', 'ignore')

        should_be_false = em.parse_attempt(5)
        self.assertFalse(should_be_false)


    def test_parse_soft_state(self):
        #Since we are passing the default, handle on soft it's not desirable
        em = EventHandler('OK', 'SOFT', '1', 'AB-Infasa', 'ignore')


        should_be_false = em.parse_soft_attempt()
        self.assertFalse(should_be_false)

    def test_parse_soft_state_wrong_soft_attempt(self):

        #Should be false because the attempt it's below the acceptable. pss: 3
        em = EventHandler('CRITICAL', 'SOFT', '2', 'AB-Infasa', 'ignore', 'CRITICAL', 3)

        should_be_false = em.parse_soft_attempt()
        self.assertFalse(should_be_false)

    def test_parse_soft_state_soft_attempt(self):

        #Should be false because the attempt it's below the acceptable. pss: 3
        em = EventHandler('CRITICAL', 'SOFT', '4', 'AB-Infasa', 'ignore', 'CRITICAL', 3)

        should_be_true = em.parse_soft_attempt()
        self.assertTrue(should_be_true)

    def test_parse_soft_state_soft_attempt_wrong_state(self):

        #Should be false because the attempt it's below the acceptable. pss: 3
        em = EventHandler('WARNING', 'SOFT', '4', 'AB-Infasa', 'ignore', 'CRITICAL', 3)

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

        #Issue 1 = Ignore attempt in hard state
        should_be_true = em.parse_hard_attempt()
        self.assertTrue(should_be_true)


    def test_should_call_handler_hard_state_right_state_and_attempt(self):

        em = EventHandler('CRITICAL', 'HARD', '4', 'AB-Infasa', 'ignore')

        should_be_true = em.should_call_handler()
        self.assertTrue(should_be_true)

    def test_should_call_handler_soft_state_wrong_attempt(self):
        # This is true for HARD state but we passed soft state
        em = EventHandler('CRITICAL', 'SOFT', '2', 'AB-Infasa', 'ignore')

        should_be_false = em.should_call_handler()
        self.assertFalse(should_be_false)

    def test_should_call_handler_soft_state_right_attempt(self):
        # Default for soft attempt is 3
        em = EventHandler('CRITICAL', 'SOFT', '3', 'AB-Infasa', 'ignore')

        should_be_true = em.should_call_handler()
        self.assertTrue(should_be_true)

    def test_should_call_handler_hard_state_right_state_and_ignore_attempt(self):
        # This is true for HARD state but we pass soft state
        em = EventHandler('CRITICAL', 'HARD', '20', 'AB-Infasa', 'ignore', 'CRITICAL', 3)

        should_be_true = em.should_call_handler()
        self.assertTrue(should_be_true)