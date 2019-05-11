package com.zenterio.jenkins.jobtype


class JobTypeCollectArtifacts extends JobType {
    public JobTypeCollectArtifacts() {
        super('Collect Artifacts', 'art', 'Collect all artifacts from all jobs in a build-flow.')
    }
}
