#!/usr/bin/env python2
#

# Tag a drop build, requires Jenkins builds that build from tags.
#

import requests
import build
import argparse
import git
import shutil

api_pattern='http://{0}/job/{1}/{2}/api/python'

def parse_arguments():
    parser = argparse.ArgumentParser(description='Set a drop tag from a Jenkins build')
    parser.add_argument('newtag')
    parser.add_argument('server')
    parser.add_argument('jobname')
    parser.add_argument('buildnumber')
    return parser.parse_args()

    
if __name__ == "__main__":
    args = parse_arguments()
    r = requests.get(api_pattern.format(args.server, args.jobname, args.buildnumber))
    thebuild = build.Build()
    thebuild.set_jobdata(r.text)

    source_tag = thebuild.get_parameter('tag')

    if len(thebuild.get_git_repositories()) == 0:
        print "No git repositories found."
    else:
        print "Setting tag "+args.newtag+ " on build tag "+source_tag
        for repourl in thebuild.get_git_repositories():
            print repourl
            shutil.rmtree('repo', True)
            repo=git.Repo.clone_from(repourl,'repo')
            repo.git.checkout(source_tag)
            repo.create_tag(args.newtag)
            #repo.remotes.origin.push()

# python tagdrop.py newtag linsci01:8080 product-develop-compile-ZEN_NAVI_BCM7356 2

# Alternative use in Jenkins:
# newtag from NEW_TAG
# server from JENKINS_URL (set in system)
# jobname from JOB_NAME
# build_no from BUILD_NO
