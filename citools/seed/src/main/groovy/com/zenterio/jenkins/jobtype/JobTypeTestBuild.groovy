package com.zenterio.jenkins.jobtype

class JobTypeTestBuild extends JobType {

    public JobTypeTestBuild() {
        super("test","tst","Run tests on the software.")
    }

    JobTypeTestBuild(String name, String shortName, String description) {
        super(name, shortName, description)
    }
}
