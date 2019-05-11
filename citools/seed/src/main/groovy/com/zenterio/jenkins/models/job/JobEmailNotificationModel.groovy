package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.ProjectManager
import com.zenterio.jenkins.configuration.TechLead
import com.zenterio.jenkins.configuration.ContactInformationCollection
import com.zenterio.jenkins.models.ModelProperty

class JobEmailNotificationModel extends ModelProperty {

    JobEmailNotificationPolicy policy
    ContactInformationCollection watchers
    ContactInformationCollection owners
    ProjectManager pm
    TechLead techLead
    String customContent

    public JobEmailNotificationModel(JobEmailNotificationPolicy policy,
            ContactInformationCollection watchers,
            ProjectManager pm, TechLead techLead,
            String customContent="", ContactInformationCollection owners=null) {
        super()
        this.policy = policy
        this.watchers = watchers
        this.pm = pm
        this.techLead = techLead
        this.customContent = customContent
        this.owners = owners ?: new ContactInformationCollection()
    }
}
