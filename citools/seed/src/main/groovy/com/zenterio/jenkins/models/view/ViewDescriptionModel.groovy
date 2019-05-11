package com.zenterio.jenkins.models.view

import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.models.common.DescriptionModel
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.JenkinsUrl
import com.zenterio.jenkins.JobName


class ViewDescriptionModel extends DescriptionModel {

    protected Project project
    protected JenkinsUrl url
    protected JobName jobName
    protected JenkinsUrl incUrl
    protected JobName incJobName

    public ViewDescriptionModel(Project project,
        JenkinsUrl url, JobName jobName,
        JenkinsUrl incUrl, JobName incJobName) {
        super("")
        this.project = project
        this.url = url
        this.jobName = jobName
        this.incUrl = incUrl
        this.incJobName = incJobName
    }

    @Override
    public String getDescription() {
        String result ="""
<div style='display: inline-block; min-width: 400px; max-width: 40%; vertical-align: top; margin: 10px; border: 1px solid #bbbbbb; padding: 10px 10px; background: #f0f0f0; border-radius:10px; box-shadow: 5px 5px 5px #888888;'>
    <table border="0" style="border-spacing: 10px 0px; border-collapse: separate;">
        <tr>
            <td style="vertical-align: top;">
                <h4>Origins</h4>
                <ul>
                ${
                    project.origins.collect { origin ->
                        "<li><a href='${this.url.getUrl(origin)}'>${origin.name}</a>${this.getIncrementalDescripton(origin)}</li>"
                    }.join('\n                ')
                }
                </ul>
            <td/>
            <td>
              <p style='background: inherit'>
                Project Manager: <a href='mailto:${this.project.pm.email}'>${this.project.pm.name}</a><br/>
                Tech-lead: <a href='mailto:${this.project.techLead.email}'>${this.project.techLead.name}</a><br/>
              </p>
              ${this.renderWatchersHtml(project.watchers)}
           </td>
        </tr>
    </table>
</div>
"""
        return result
    }

    private String getIncrementalDescripton(Origin origin) {
        if (origin.isIncrementalActive()) {
            return " (<a href='${this.incUrl.getUrl(origin)}'>incremental</a>)"
        }
        else {
            return ""
        }
    }

}
