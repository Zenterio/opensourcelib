package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.Upstream
import com.zenterio.jenkins.models.IModel

class TestJobModel extends CompileJobModel {

    protected IModel testTrigger
    protected Upstream upstream
    protected JobModel parentJob

    public TestJobModel(Upstream upstream, JobModel parentJob) {
        this.upstream = upstream
        this.parentJob = parentJob
    }

    @Override
    protected void onSetParent(IModel parent) {
        String testJobName = this.getChild(JobNameModel)?.name
        JobLabelModel jobLabelModel = (JobLabelModel)this.getChild(JobLabelModel)
        if (this.upstream == Upstream.ASYNC) {
            this.testTrigger = new JobDownStreamTriggerModel(
                    [new DownStreamTriggerParameter(
                            testJobName, 'ALWAYS', jobLabelModel)]
                            as DownStreamTriggerParameter[], false)

            if (this.parentJob) {
                parent = this.parentJob
            }
            parent << this.testTrigger
        }
    }

    @Override
    protected void onUnsetParent(IModel oldParent) {
        if (this.parentJob) {
            oldParent = this.parentJob
        }
        oldParent.removeChild(this.testTrigger)
    }
}
