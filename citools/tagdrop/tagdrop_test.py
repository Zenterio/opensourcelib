#!/usr/bin/env python2
#

import unittest
import tagdrop

class TestBuild(unittest.TestCase):

    def setUp(self):
        self.build = tagdrop.Build()

    def tearDown(self):
        self.build = None

    def test_set_jobdata_empty(self):
        self.build.set_jobdata("{}")
        self.assertTrue(self.build.jobdata == {})

#    def test_set_jobdata_malformed_throws_Valueerror(self):
#        with self.assertRaises(ValueError):
#            self.build.set_jobdata("{bar}")
#
#    def test_set_jobdata_malformed_throws_SyntaxError(self):
#        with self.assertRaises(SyntaxError):
#            self.build.set_jobdata("{'foo':bar}")
        
    def test_get_parameters_no_jobdata(self):
        self.build.set_jobdata("{\"none\":None}")
        self.assertTrue(len(self.build.get_parameters()) == 0 )

if __name__ == "__main__":
    unittest.main()
