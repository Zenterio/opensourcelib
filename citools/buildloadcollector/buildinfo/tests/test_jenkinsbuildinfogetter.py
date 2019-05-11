import datetime

from copy import deepcopy

from jenkinsapi.custom_exceptions import NoBuildData

from jenkinsbuildinfogetter import JenkinsBuildInfoGetter
from unittest import TestCase


class MockBuild:

    def __init__(self,
                 timestamp=datetime.datetime(2016, 4, 6, 14, 35, 45),
                 duration=datetime.timedelta(seconds=5),
                 actions={'queuingDurationMillis': 5, 'parameters': [{'name': 'test', 'value': 'fake'}]},
                 slave="test",
                 number=9,
                 status="SUCCESS",
                 running=False):
        self.timestamp = timestamp
        self.duration = duration
        self.actions = deepcopy(actions)
        self.slave = slave
        self.number = number
        self.status = status
        self.running = running

    def get_timestamp(self):
        return self.timestamp

    def get_duration(self):
        return self.duration

    def get_actions(self):
        return self.actions

    def get_slave(self):
        return self.slave

    def get_number(self):
        return self.number

    def get_status(self):
        return self.status

    def is_running(self):
        return self.running


class MockJob:

    def __init__(self, last_build=None, num_builds=9, name='test'):
        self.num_builds = num_builds
        self.name = name
        self.builds = [MockBuild(number=i) for i in self._get_build_numbers()]
        if last_build:
            self.builds[-1] = last_build

    def get_last_build(self):
        return self.builds[-1]

    def get_build(self, num):
        return self.builds[num-1]

    def get_build_dict(self):
        build_dict = {}
        for i in range(1, self.num_builds+1):
            build_dict[i] = self.name
        return build_dict

    def get_build_ids(self):
        """
        :return: [build_num, build_num-1, ..., 2, 1]
        """
        return reversed(self._get_build_numbers())

    def _get_build_numbers(self):
        return list(range(1, self.num_builds+1))


class MockJobWithNoBuilds(MockJob):

    def __init__(self):
        super().__init__(num_builds=0)


class MockJenkins:

    def __init__(self, jobs=[('test', MockJob())]):
        self.jobs = deepcopy(jobs)

    def get_jobs(self):
        return self.jobs


class TestBuildInfoGetter(TestCase):

    def setUp(self):
        self.loader = JenkinsBuildInfoGetter(server=None)
        self.loader._jenkins = MockJenkins()
        self.job = MockJob()
        self.build = MockBuild()

    def tearDown(self):
        self.loader = None
        self.job = None
        self.build = None

    def test_load_build_info_job_with_no_builds(self):
        self.loader._jenkins = MockJenkins([('test1', MockJob()),
                                            ('test2', MockJobWithNoBuilds())])
        data, reference = self.loader.load_build_info()
        self.assertTrue('test1' in data)
        self.assertFalse('test2' in data)
        self.assertTrue('test1' in reference)
        self.assertFalse('test2' in reference)

    def test_load_build_info_without_reference_gets_all_builds_and_returns_reference_one_job(self):
        expectedreference = {'test': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                       'Start Time': '2016-04-06T14:35:45',
                                       'Build number': 9,
                                       'Parameters': [('test', 'fake')],
                                       'End Time': '2016-04-06T14:35:50',
                                       'Node': 'test',
                                       'Status': 'SUCCESS'}]}
        data, reference = self.loader.load_build_info()
        self.assertEqual(len(data['test']), 9)
        self.assertEqual(reference, expectedreference)

    def test_load_build_info_skips_running_build(self):
        job = MockJob(num_builds=5)
        job.get_last_build().running = True
        self.loader._jenkins = MockJenkins([('test', job)])
        data, reference = self.loader.load_build_info()

        self.assertEqual(len(data), 1)
        self.assertEqual(len(reference), 1)
        self.assertEqual(len(data['test']), 4)
        self.assertEqual(len(reference['test']), 1)
        self.assertEqual(reference['test'][0]['Build number'], 4)

    def test_load_build_info_skips_running_build_when_having_a_reference_build(self):
        reference = {'test': [{'Queue Time': '2016-04-06T14:35:44.995000',
                               'Start Time': '2016-04-06T14:35:45',
                               'Build number': 3,
                               'Parameters': [('test', 'fake')],
                               'End Time': '2016-04-06T14:35:50',
                               'Node': 'test',
                               'Status': 'SUCCESS'}]}
        job = MockJob(num_builds=5)
        job.get_last_build().running = True
        self.loader._jenkins = MockJenkins([('test', job)])
        self.loader._previousdata = reference
        data, reference = self.loader.load_build_info()

        self.assertEqual(len(data), 1)
        self.assertEqual(len(reference), 1)
        self.assertEqual(len(data['test']), 1)
        self.assertEqual(data['test'][0]['Build number'], 4)
        self.assertEqual(len(reference['test']), 1)
        self.assertEqual(reference['test'][0]['Build number'], 4)


    def test_load_build_info_with_reference_gets_newer_builds_one_job(self):
        expectedreference = {'test': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                       'Start Time': '2016-04-06T14:35:45',
                                       'Build number': 9,
                                       'Parameters': [('test', 'fake')],
                                       'End Time': '2016-04-06T14:35:50',
                                       'Node': 'test',
                                       'Status': 'SUCCESS'}]}
        reference = {'test': [{'Queue Time': '2016-04-06T14:35:44.995000',
                               'Start Time': '2016-04-06T14:35:45',
                               'Build number': 3,
                               'Parameters': [('test', 'fake')],
                               'End Time': '2016-04-06T14:35:50',
                               'Node': 'test',
                               'Status': 'SUCCESS'}]}
        self.loader._previousdata = reference
        data, reference = self.loader.load_build_info()
        self.assertEqual(len(data['test']), 6)
        self.assertEqual(expectedreference, reference)

    def test_load_build_info_without_reference_gets_all_builds_and_returns_reference_two_jobs(self):
        self.loader._jenkins = MockJenkins([('test1', MockJob()), ('test2', MockJob(num_builds=5))])
        expectedreference = {'test1': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                        'Start Time': '2016-04-06T14:35:45',
                                        'Build number': 9,
                                        'Parameters': [('test', 'fake')],
                                        'End Time': '2016-04-06T14:35:50',
                                        'Node': 'test',
                                        'Status': 'SUCCESS'}],
                             'test2': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                        'Start Time': '2016-04-06T14:35:45',
                                        'Build number': 5,
                                        'Parameters': [('test', 'fake')],
                                        'End Time': '2016-04-06T14:35:50',
                                        'Node': 'test',
                                        'Status': 'SUCCESS'}]}
        data, reference = self.loader.load_build_info()
        self.assertEqual(len(data['test1']), 9)
        self.assertEqual(len(data['test2']), 5)
        self.assertEqual(reference, expectedreference)

    def test_load_build_info_with_reference_gets_newer_builds_and_returns_reference_two_jobs(self):
        self.loader._jenkins = MockJenkins([('test1', MockJob()), ('test2', MockJob(num_builds=5))])
        expectedreference = {'test1': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                        'Start Time': '2016-04-06T14:35:45',
                                        'Build number': 9,
                                        'Parameters': [('test', 'fake')],
                                        'End Time': '2016-04-06T14:35:50',
                                        'Node': 'test',
                                        'Status': 'SUCCESS'}],
                             'test2': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                        'Start Time': '2016-04-06T14:35:45',
                                        'Build number': 5,
                                        'Parameters': [('test', 'fake')],
                                        'End Time': '2016-04-06T14:35:50',
                                        'Node': 'test',
                                        'Status': 'SUCCESS'}]}
        reference = {'test1': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                'Start Time': '2016-04-06T14:35:45',
                                'Build number': 5,
                                'Parameters': [('test', 'fake')],
                                'End Time': '2016-04-06T14:35:50',
                                'Node': 'test',
                                'Status': 'SUCCESS'}],
                     'test2': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                'Start Time': '2016-04-06T14:35:45',
                                'Build number': 3,
                                'Parameters': [('test', 'fake')],
                                'End Time': '2016-04-06T14:35:50',
                                'Node': 'test',
                                'Status': 'SUCCESS'}]}
        self.loader._previousdata = reference
        data, reference = self.loader.load_build_info()
        self.assertEqual(len(data['test1']), 4)
        self.assertEqual(len(data['test2']), 2)
        self.assertEqual(reference, expectedreference)

    def test_load_build_info_with_incomplete_reference_gets_newer_builds_and_all_for_missing(self):
        self.loader._jenkins = MockJenkins([('test1', MockJob()), ('test2', MockJob(num_builds=5))])
        expectedreference = {'test1': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                        'Start Time': '2016-04-06T14:35:45',
                                        'Build number': 9,
                                        'Parameters': [('test', 'fake')],
                                        'End Time': '2016-04-06T14:35:50',
                                        'Node': 'test',
                                        'Status': 'SUCCESS'}],
                             'test2': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                        'Start Time': '2016-04-06T14:35:45',
                                        'Build number': 5,
                                        'Parameters': [('test', 'fake')],
                                        'End Time': '2016-04-06T14:35:50',
                                        'Node': 'test',
                                        'Status': 'SUCCESS'}]}
        reference = {'test1': [{'Queue Time': '2016-04-06T14:35:44.995000',
                                'Start Time': '2016-04-06T14:35:45',
                                'Build number': 5,
                                'Parameters': [('test', 'fake')],
                                'End Time': '2016-04-06T14:35:50',
                                'Node': 'test',
                                'Status': 'SUCCESS'}]}
        self.loader._previousdata = reference
        data, reference = self.loader.load_build_info()
        self.assertEqual(len(data['test1']), 4)
        self.assertEqual(len(data['test2']), 5)
        self.assertEqual(reference, expectedreference)

    def test_get_new_builds_gets_new_builds(self):
        indata = {'test': [{'Build number': 1}]}
        ret = {}
        self.loader._previousdata = indata
        self.assertEqual(len(self.loader._previousdata['test']), 1)
        self.loader._get_new_builds(self.job, 'test', MockBuild(), ret)
        self.assertEqual(len(ret['test']), 8)
        self.assertNotIn(indata['test'], ret['test'])

    def test_get_all_builds_from_job_gets_all_builds(self):
        data = {}
        self.loader._get_all_builds_from_job(data, self.job, 'test')
        self.assertEqual(len(data['test']), 9)

    def test_get_data_from_build_gets_data(self):
        expected = {'Parameters': [('test', 'fake')],
                    'End Time': '2016-04-06T14:35:50',
                    'Queue Time': '2016-04-06T14:35:44.995000',
                    'Start Time': '2016-04-06T14:35:45',
                    'Build number': 9,
                    'Node': 'test',
                    'Status': 'SUCCESS'}
        result = self.loader._get_data_from_build(self.build)
        self.assertEqual(expected, result)

    def test_get_data_from_build_missing_queuetime_returns_none(self):
        self.build.actions.pop('queuingDurationMillis')
        expected = {'Parameters': [('test', 'fake')],
                    'End Time': '2016-04-06T14:35:50',
                    'Queue Time': None,
                    'Start Time': '2016-04-06T14:35:45',
                    'Build number': 9,
                    'Node': 'test',
                    'Status': 'SUCCESS'}
        result = self.loader._get_data_from_build(self.build)
        self.assertEqual(expected, result)

    def test_get_data_from_build_missing_parameters_returns_empty_list(self):
        self.build.actions.pop('parameters')
        expected = {'Parameters': [],
                    'End Time': '2016-04-06T14:35:50',
                    'Queue Time': '2016-04-06T14:35:44.995000',
                    'Start Time': '2016-04-06T14:35:45',
                    'Build number': 9,
                    'Node': 'test',
                    'Status': 'SUCCESS'}
        result = self.loader._get_data_from_build(self.build)
        self.assertEqual(expected, result)

