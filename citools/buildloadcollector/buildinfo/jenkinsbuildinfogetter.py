import datetime
import traceback

import requests
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.custom_exceptions import NoBuildData


class JenkinsBuildInfoGetter:
    def __init__(self, server, previousdata=None, ssl_verify=True):
        self._previousdata = {} if previousdata is None else previousdata
        self._jenkins = None
        self._server = server
        self._ssl_verify = ssl_verify

    def set_previousdata(self, previousdata):
        self._previousdata = previousdata

    def _connect(self):
        self._jenkins = Jenkins(self._server, ssl_verify=self._ssl_verify)

    def load_build_info(self):
        if self._jenkins is None:
            self._connect()
        jobs = self._jenkins.get_jobs()
        return self._get_build_info_from_jobs(jobs)

    def _get_build_info_from_jobs(self, jobs):
        data = {}
        reference = {}
        for jobname, job in jobs:
            try:
                latest_build = self._get_latest_not_running_build(job)
                if latest_build is None:
                    continue
            except requests.exceptions.HTTPError:  # if we get connection issues mid-load we don't want to abort everything
                print("Could not load latest build for job {jobname} due to connection error".format(jobname=jobname))
                print(traceback.format_exc())
            reference.setdefault(jobname, []).append(self._get_data_from_build(latest_build))
            if jobname in self._previousdata:
                self._get_new_builds(job, jobname, latest_build, data)
            else:
                self._get_all_builds_from_job(data, job, jobname)
        return data, reference

    def _get_all_builds_from_job(self, data, job, jobname):
        for build_id in job.get_build_ids():
            build = job.get_build(build_id)
            if self.include_build(build):
                data.setdefault(jobname, []).append(self._get_data_from_build(job.get_build(build_id)))

    def _get_new_builds(self, job, jobname, latestbuild, data):
        last_saved_build_number = max([x['Build number'] for x in self._previousdata[jobname]])
        if last_saved_build_number < latestbuild.get_number():
            for num in range(last_saved_build_number + 1, latestbuild.get_number() + 1):
                try:
                    build = job.get_build(num)
                    if self.include_build(build):
                        data.setdefault(jobname, []).append(self._get_data_from_build(job.get_build(num)))
                except requests.exceptions.HTTPError:  # if we get connection issues mid-load we don't want to abort everything
                    print("Job {jobname} build {num} failed to load".format(jobname=jobname, num=num))
                    print(traceback.format_exc())
                except KeyError:  # Not all jobs between last saved and latest exist
                    print("Job {jobname} build {num} was not available".format(jobname=jobname, num=num))

    @staticmethod
    def _get_data_from_build(build):
        starttime = build.get_timestamp()
        duration = build.get_duration()
        endtime = starttime + duration
        try:
            actions = build.get_actions()
        except ValueError:  # Builds can have malformed parameters, crashing get_actions()
            actions = None
        queuetime = None
        if actions is not None:
            queuetime = actions.get('queuingDurationMillis')
            if queuetime is not None:
                queuetime = datetime.timedelta(milliseconds=queuetime)
                queuetime = (starttime - queuetime).isoformat()
        node = build.get_slave()
        buildnumber = build.get_number()
        parameters = []
        status = build.get_status()
        if actions is not None:
            for param in actions.get('parameters', []):
                parameters.append((param['name'], param['value']))
        return {'Queue Time': queuetime,
                'Start Time': starttime.isoformat(),
                'End Time': endtime.isoformat(),
                'Node': node,
                'Build number': buildnumber,
                'Parameters': parameters,
                'Status': status}

    def _get_latest_not_running_build(self, job):
        for build_id in job.get_build_ids():
            build = job.get_build(build_id)
            if self.include_build(build):
                return build
        # If build has not yet been run, or if none of the run builds are of interest, return None
        return None

    @staticmethod
    def include_build(build):
        return not build.is_running()
