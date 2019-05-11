package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.Upstream
import com.zenterio.jenkins.models.IModel


class CoverityJobModel extends CompileJobModel {

    protected IModel coverityTrigger

    protected Upstream upstream

    protected JobModel parentJob

    public CoverityJobModel(Upstream upstream, JobModel parentJob) {
        this.upstream = upstream
        this.parentJob = parentJob
    }


    @Override
    protected void onSetParent(IModel parent) {
        String coverityJobName = this.getChild(JobNameModel)?.name
        JobLabelModel jobLabelModel = (JobLabelModel)this.getChild(JobLabelModel)
        if (this.upstream == Upstream.ASYNC) {
            this.coverityTrigger = new JobDownStreamTriggerModel(
                    [new DownStreamTriggerParameter(
                            coverityJobName, 'ALWAYS', jobLabelModel)]
                            as DownStreamTriggerParameter[], false)

            if (this.parentJob) {
                parent = this.parentJob
            }
            parent << this.coverityTrigger
        }
    }

    @Override
    protected void onUnsetParent(IModel oldParent) {
        if (this.parentJob) {
            oldParent = this.parentJob
        }
        oldParent.removeChild(this.coverityTrigger)
    }
}
