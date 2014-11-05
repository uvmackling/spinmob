"""
Test code for _wc_daq_object.py module.
"""


import os
import numpy as _np

import daqmx._daq_objects as daq_object

import unittest as _ut
from unittest import TestLoader as _TL



def test():
    """
    Run all tests in this module.
    """

    suite_do_task   = _TL().loadTestsFromTestCase(Test_do_task)
#    suite_task_base = _TL().loadTestsFromTestCase(Test_task_base)

    suites = [suite_do_task]  
    
    alltests = _ut.TestSuite(suites)
    _ut.TextTestRunner(verbosity=0).run(alltests)
    
    
    
class Test_do_task(_ut.TestCase): 
    """
    Test digital output task object
    """
    
    def setUp(self):
        self.do_task = daq_object.do_task()  
        
        # Get the settings dictionary default values
        # for ease of testing.
        self.settings = self.do_task.settings


    def tearDown(self):
        self.do_task = None
        self.settings = None


    def test_settingsDefault_name(self):

        out = self.settings['do_task_name']
        val = "Default Output Task"

        self.assertEqual(val, out)        
        

    def test_settingsDefault_timeout(self):

        out = self.settings['do_timeout']
        val = 5.0

        self.assertEqual(val, out) 


    def test_settingsDefault_channels(self):

        out = self.settings['do_channels']
        val = "/PXI1Slot2/port0/line0:7"

        self.assertEqual(val, out) 


    def test_settingsDefault_rate(self):

        out = self.settings['do_rate']
        val = 1000000

        self.assertEqual(val, out) 


    def test_settingsDefault_clock_source(self):

        out = self.settings['do_clock_source']
        val = "OnboardClock"

        self.assertEqual(val, out) 


    def test_settingsDefault_trigger_source(self):

        out = self.settings['do_trigger_source']
        val = "/PXI1Slot2/100kHzTimebase"

        self.assertEqual(val, out) 

















