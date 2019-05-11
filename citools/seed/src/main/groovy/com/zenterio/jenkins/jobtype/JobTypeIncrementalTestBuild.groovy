package com.zenterio.jenkins.jobtype

class JobTypeIncrementalTestBuild extends JobType {

    JobTypeIncrementalTestBuild() {
        super('incremental-test', 'inc-tst', 'Run tests on the software from incremental builds.')
    }
}
