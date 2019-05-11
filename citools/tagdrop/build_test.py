#!/usr/bin/env python2
#

import unittest
import build

class TestBuild(unittest.TestCase):

    def setUp(self):
        self.build = build.Build()

    def tearDown(self):
        self.build = None

    def test_set_jobdata_empty(self):
        self.build.set_jobdata("{}")
        self.assertTrue(self.build._jobdata == {})

    def test_set_jobdata_malformed_throws_Valueerror(self):
        with self.assertRaises(ValueError):
            self.build.set_jobdata("{bar}")

    def test_set_jobdata_malformed_throws_SyntaxError(self):
        with self.assertRaises(SyntaxError):
            self.build.set_jobdata('{"actions":[{"parameters":[{"name":"tag","value":"jenkins-jdsl-trigger-6"}]}')

    def test_get_parameters_empty_config_no_parameters(self):
        self.build.set_jobdata("{}")
        self.assertTrue(self.build.get_parameters()=={})

    def test_get_parameters_two_parameters(self):
        self.build.set_jobdata('{"actions":[{"notparameters":[{"name":"tag","value":"not a tag"}]},{"parameters":[{"name":"tag","value":"value"},{"name":"parameter2","value":"value2"}]}]}')
        self.assertTrue(self.build.get_parameters()==
                        {'tag': 'value', 'parameter2': 'value2'})

    def test_get_parameter_missing_throws_KeyError(self):
        self.build.set_jobdata('{"actions":[{"parameters":[{"name":"tag","value":"value"},{"name":"parameter2","value":"value2"}]}]}')
        with self.assertRaises(KeyError):
            self.build.get_parameter('missing')

    def test_get_parameter(self):
        self.build.set_jobdata('{"actions":[{"parameters":[{"name":"tag","value":"value"},{"name":"parameter2","value":"value2"}]}]}')
        self.assertTrue(self.build.get_parameter('parameter2') ==
                        'value2')
        self.assertTrue(self.build.get_parameter('tag') ==
                        'value')


    def test_get_repositories(self):
        self.build.set_jobdata("""{"actions":[{"buildsByBranchName":{"zids/tags/jenkins-jdsl-trigger-6":{"buildNumber":2,
                                                                       "buildResult":None,
                                                                       "marked":{"SHA1":"4759ae1c74b8b9a505fcf5ff4929927e1c90428a",
                                                                                 "branch":[{"SHA1":"4759ae1c74b8b9a505fcf5ff4929927e1c90428a",
                                                                                            "name":"zids/tags/jenkins-jdsl-trigger-6"}]},
                                                                       "revision":{"SHA1":"4759ae1c74b8b9a505fcf5ff4929927e1c90428a",
                                                                                   "branch":[{"SHA1":"4759ae1c74b8b9a505fcf5ff4929927e1c90428a",
                                                                                              "name":"zids/tags/jenkins-jdsl-trigger-6"}]}}},
             "lastBuiltRevision":{"SHA1":"4759ae1c74b8b9a505fcf5ff4929927e1c90428a",
                                  "branch":[{"SHA1":"4759ae1c74b8b9a505fcf5ff4929927e1c90428a",
                                             "name":"zids/tags/jenkins-jdsl-trigger-6"}]},
             "remoteUrls":["git@git.zenterio.lan:user-torax-public-zids"],
             "scmName":""},
            {},
            {"buildsByBranchName":{"fs/tags/jenkins-jdsl-trigger-6":{"buildNumber":2,
                                                                     "buildResult":None,
                                                                     "marked":{"SHA1":"bcc20c2f138c91c24174e1621820ced1fe13f944",
                                                                               "branch":[{"SHA1":"bcc20c2f138c91c24174e1621820ced1fe13f944",
                                                                                          "name":"fs/tags/jenkins-jdsl-trigger-6"}]},
                                                                     "revision":{"SHA1":"bcc20c2f138c91c24174e1621820ced1fe13f944",
                                                                                 "branch":[{"SHA1":"bcc20c2f138c91c24174e1621820ced1fe13f944",
                                                                                            "name":"fs/tags/jenkins-jdsl-trigger-6"}]}}},
             "lastBuiltRevision":{"SHA1":"bcc20c2f138c91c24174e1621820ced1fe13f944",
                                  "branch":[{"SHA1":"bcc20c2f138c91c24174e1621820ced1fe13f944",
                                             "name":"fs/tags/jenkins-jdsl-trigger-6"}]},
             "remoteUrls":["git@git.zenterio.lan:user-torax-public-fs"],
             "scmName":""},
            {},
            {},
            {},
            {"level":None,
             "levelValue":0}]}""")
        self.assertTrue(self.build.get_git_repositories() ==
                        {"git@git.zenterio.lan:user-torax-public-fs", 
                         "git@git.zenterio.lan:user-torax-public-zids"})

if __name__ == "__main__":
    unittest.main()
