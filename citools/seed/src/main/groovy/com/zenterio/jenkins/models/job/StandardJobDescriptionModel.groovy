package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.BaseProduct
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.ContactInformationCollection
import com.zenterio.jenkins.jobtype.JobType


class StandardJobDescriptionModel extends JobDescriptionModel {

    protected BaseProduct product
    protected JobType jobType
    protected BuildType buildType
    protected ContactInformationCollection watchers
    protected ContactInformationCollection owners

    public StandardJobDescriptionModel(BaseProduct product, JobType jobType,
            BuildType buildType, ContactInformationCollection watchers, ContactInformationCollection owners=null) {
        super("")
        this.product = product
        this.jobType = jobType
        this.buildType = buildType
        this.watchers = watchers ?: new ContactInformationCollection()
        this.owners = owners ?: new ContactInformationCollection()
    }

    public StandardJobDescriptionModel(JobType jobType) {
        super("")
        this.jobType = jobType
        this.product = null
        this.buildType = null
        this.watchers = new ContactInformationCollection()
        this.owners = new ContactInformationCollection()
    }

    public String getDescription() {

        /*
         * When modifying this section, please have in mind that not all fields
         * are always set. The description must make sense, both code-wise and
         * generated output with/without individual fields.
         */

        String desc = """\
<div style='display: inline-block; min-width: 400px; max-width: 40%; vertical-align: top; margin: 10px; border: 1px solid #bbbbbb; padding: 5px 10px; background: #f0f0f0; border-radius:10px; box-shadow: 5px 5px 5px #888888;'>
    <p style='background: inherit'>
        ${(this.jobType) ? this.jobType.description : ""}
        ${(this.buildType) ? this.buildType.description : ""}
    </p>
    ${this.renderWatchersHtml(watchers)}
    ${this.renderOwnersHtml(owners)}
</div>
"""
        return desc
    }
}
