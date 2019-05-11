package com.zenterio.jenkins

import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.BaseProduct
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.TestContext
import com.zenterio.jenkins.jobtype.JobType

class JenkinsUrl {

    private final JobName jobName

    public JenkinsUrl(String identifier = "") {
        this.jobName = new JobName(identifier)
    }

    public String getUrl(Project project) {
        return "/view/${this.jobName.getName(project)}"
    }

    public String getUrl(Origin origin) {
        Project p = origin.project
        return "${getUrl(p)}/job/${this.jobName.getName(origin)}"
    }

    public String getUrl(BaseProduct product) {
        Project p = product.origin.project
        return "${getUrl(p)}/job/${this.jobName.getName(product)}"
    }

    public String getUrl(Origin origin, JobType jobType) {
        Project p = origin.project
        return "${this.getUrl(p)}/job/${this.jobName.getName(origin, jobType)}"
    }

    public String getUrl(Project project, JobType jobType) {
        return "${this.getUrl(project)}/job/${this.jobName.getName(project, jobType)}"
    }

    public String getUrl(BaseProduct product, JobType jobType, BuildType buildType) {
        Project p = product.origin.project
        String jobName = this.jobName.getName(product, jobType, buildType)
        return "${this.getUrl(p)}/job/${jobName}"
    }

    public String getUrl(BaseProduct product, JobType jobType, BuildType buildType, TestContext testContext) {
        Project p = product.origin.project
        String jobName = this.jobName.getName(product, jobType, buildType, testContext)
        return "${this.getUrl(p)}/job/${jobName}"
    }
}
