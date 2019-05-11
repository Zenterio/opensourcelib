#! /usr/bin/env python3
import argparse
import csv
import datetime
import json
import sys

from jenkinsbuildinfogetter import JenkinsBuildInfoGetter


class BuildInfoCLI:
    def __init__(self, argv):
        self._argv = argv
        self._create_parser()
        self._args = self._parser.parse_args(argv[1:])
        self._refinput = self._args.refinput
        self._refoutput = self._args.refoutput
        self._csvoutput = self._args.csvoutput
        self._jenkins = self._args.jenkins
        self._ssl_verify = self._args.ssl_verify

    def _create_parser(self):
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument('--refinput',
                                  default="ref.json",
                                  help="Json file to read latest saved builds from, default ref.json")
        self._parser.add_argument('--refoutput',
                                  default="ref.json",
                                  help="Json file to store latest saved builds in, default ref.json")
        self._parser.add_argument('--csvoutput',
                                  default="{date}.csv".format(date=datetime.datetime.now().strftime("%Y%m%d %H-%M-%S")),
                                  help="CSVfile to store results in, default 'current date'.csv")
        self._parser.add_argument('jenkins',
                                  help="Jenkins server to get data from")
        self._parser.add_argument('--disable_ssl',
                                  dest='ssl_verify',
                                  action='store_false',
                                  help="Skip ssl verification, in case of cert issues")

    def get_reference_input_file(self):
        return self._refinput

    def get_reference_output_file(self):
        return self._refoutput

    def get_data_output_file(self):
        return self._csvoutput

    def get_jenkins_url(self):
        return self._jenkins

    def get_ssl_verify(self):
        return self._ssl_verify


class BuildInfoCSVWriter:
    def __init__(self, outfile):
        self._outfile = outfile

    def write(self, builddata):
        with open(self._outfile, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Job',
                             'Queue Time',
                             'Start Time',
                             'End Time',
                             'Build number',
                             'Parameters',
                             'Node',
                             'Status'])
            for entry in builddata:
                for build in builddata[entry]:
                    queuetime = build['Queue Time']
                    starttime = build['Start Time']
                    endtime = build['End Time']
                    buildnumber = build['Build number']
                    parameters = build['Parameters']
                    node = build['Node']
                    status = build['Status']
                    writer.writerow([entry,
                                     queuetime,
                                     starttime,
                                     endtime,
                                     buildnumber,
                                     parameters,
                                     node,
                                     status])


class BuildInfoJSONRefWriter:
    def __init__(self, outfile):
        self._outfile = outfile

    def write(self, data):
        json.dump(data, open(self._outfile, 'w'), indent=2)


class BuildInfoJSONRefReader:
    def __init__(self, infile):
        self._infile = infile

    def read(self):
        try:
            return json.load(open(self._infile, 'r'))
        except FileNotFoundError:
            return {}


if __name__ == "__main__":
    buildinfo = BuildInfoCLI(sys.argv)
    csvwriter = BuildInfoCSVWriter(buildinfo.get_data_output_file())
    refwriter = BuildInfoJSONRefWriter(buildinfo.get_reference_output_file())
    refreader = BuildInfoJSONRefReader(buildinfo.get_reference_input_file())
    jenkinsloader = JenkinsBuildInfoGetter(server=buildinfo.get_jenkins_url(),
                                           previousdata=refreader.read(),
                                           ssl_verify=buildinfo.get_ssl_verify())
    data, reference = jenkinsloader.load_build_info()
    refwriter.write(reference)
    csvwriter.write(data)


