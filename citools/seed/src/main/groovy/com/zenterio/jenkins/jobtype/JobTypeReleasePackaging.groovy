package com.zenterio.jenkins.jobtype


class JobTypeReleasePackaging extends JobType{
    public JobTypeReleasePackaging() {
        super('Release Packaging', 'pkg', 'Create a release package from the artifacts in a flow job.')
    }
}
