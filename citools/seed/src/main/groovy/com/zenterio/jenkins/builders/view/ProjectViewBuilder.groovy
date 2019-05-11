package com.zenterio.jenkins.builders.view

import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.view.*
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.JenkinsUrl
import com.zenterio.jenkins.JobName

/**
 * Assembles the model for a Project View.
 */
class ProjectViewBuilder implements IModelBuilder {

    private Project project
    private JenkinsUrl url
    private JobName jobName
    private JenkinsUrl incUrl
    private JobName incJobName
    private String scriptletsDirectory

    public ProjectViewBuilder(Project project, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, JenkinsUrl incUrl, JobName incJobName) {
        this.project = project
        this.url = url
        this.jobName = jobName
        this.incUrl = incUrl
        this.incJobName = incJobName
        this.scriptletsDirectory = scriptletsDirectory
    }

    @Override
    public IModel build() {
        ModelEntity view = new ViewModel();
        view << new ViewNameModel(this.jobName.getName(project))
        view << new ViewJobSelectionModel("${this.jobName.getName(project).toLowerCase()}-.*",
            new ArrayList<String>())

        IModel desc = new ViewDescriptionModel(project,
            this.url, this.jobName,
            this.incUrl, this.incJobName)
        view << desc << new HtmlCrumbDisplayModel(project.name)
        view << desc << new DescriptionDisplayModel(project.description.description)

        view << new ViewColumnsModel()
        view << new ViewUrlModel(this.url.getUrl(project))
        return view;
    }
}
