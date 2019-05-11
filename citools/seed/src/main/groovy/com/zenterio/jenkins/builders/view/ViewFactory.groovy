package com.zenterio.jenkins.builders.view

import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.DisplayName
import com.zenterio.jenkins.JenkinsUrl
import com.zenterio.jenkins.JobName
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.Owner
import com.zenterio.jenkins.models.job.JobNameModel

class ViewFactory {

    private JenkinsUrl url
    private JobName jobName
    private JenkinsUrl incUrl
    private JobName incJobName
    private String scriptletsDirectory
    private Map<String,OwnerGroupViewBuilder> ownerGroups
    private OwnerlessViewBuilder ownerless

    public ViewFactory(String scriptletsDirectory, JenkinsUrl url,
        JobName jobName, JenkinsUrl incUrl, JobName incJobName) {
        super()
        this.url = url
        this.jobName = jobName
        this.incUrl = incUrl
        this.incJobName = incJobName
        this.scriptletsDirectory = scriptletsDirectory
        this.ownerGroups = [:]
        this.ownerless = new OwnerlessViewBuilder()
    }

    public IModel getProjView(Project project) {
        return (new ProjectViewBuilder(project,
            this.scriptletsDirectory, this.url,
            this.jobName, this.incUrl, this.incJobName)).build()
    }

    public void makeOwnerGroupView(Owner owner, String jobName) {
        OwnerGroupViewBuilder ownerGroupViewBuilder = this.ownerGroups.getOrDefault(owner.group, new OwnerGroupViewBuilder(owner.group))
        ownerGroupViewBuilder.addOwner(owner)
        ownerGroupViewBuilder.addJob(jobName)
        this.ownerGroups[owner.group] = ownerGroupViewBuilder
    }

    public void makeOwnerlessView(String jobName) {
        this.ownerless.addJob(jobName)
    }

    public Map<String,OwnerGroupViewBuilder> getOwnerGroupViews() {
        return this.ownerGroups
    }

    public OwnerlessViewBuilder getOwnerlessView() {
        return this.ownerless
    }

}
