package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.common.UrlModel
import com.zenterio.jenkins.models.display.DescriptionDisplayNameModel

class ProductFlowJobDescriptionModel extends JobDescriptionModel {

    ProjectManager projectManager
    TechLead techLead
    ContactInformationCollection watchers

    public ProductFlowJobDescriptionModel(ProjectManager projectManager,
            TechLead techLead, ContactInformationCollection watchers) {
        super("")
        this.projectManager = projectManager
        this.techLead = techLead
        this.watchers = watchers
    }

    public String getDescription() {
        IModel entity = this.getParent(ModelEntity, false)
        String jobSections = [
            ["Compilation", [UnitTestJobModel, CompileJobModel]],
            ["Coverity - static code analysis", CoverityJobModel],
            ["Documentation", DocJobModel],
            ["Production Signed", SignJobModel],
            ["Test", TestJobModel]
            ].collect({ item -> getJobSection(entity, item[0], item[1]) }).findAll({ String s -> s != "" }).join("\n        ")
        String desc = """
<div style='position: relative; float: left; min-width: 40%; margin: 15px; border: 1px solid #bbbbbb; padding: 5px 5px; background: #f0f0f0; border-radius:10px; box-shadow: 5px 5px 5px #888888;'>
    <div style='position: relative; min-width: 40%; float: left; margin: 5px; padding: 5px 10px;'>
        ${jobSections}
    </div>
    <div style='position: relative; min-width: 40%; float: left; margin: 5px; padding: 5px 10px;'>
        <p style='background: #f0f0f0'>
            Project Manager: <a href='mailto:${this.projectManager.email}'>${this.projectManager.name}</a><br/>
            Tech-lead: <a href='mailto:${this.techLead.email}'>${this.techLead.name}</a><br/>
        </p>${this.renderWatchersHtml(this.watchers)}
    </div>
</div>
"""
        return desc
    }

    protected String getJobSection(IModel entity, String header, Class cls) {
        return getJobSection(entity, header, [cls])
    }

    protected String getJobSection(IModel entity, String header, List<Class> classes) {
        String listItems = entity.getChildren(classes, true, true).sort({ a, b ->
                a.getProperty(DescriptionDisplayNameModel)?.name <=>
                b.getProperty(DescriptionDisplayNameModel)?.name
            }).collect { IModel jobModel ->
                String url = jobModel.getProperty(UrlModel, false, true)?.url
                String displayName = jobModel.getProperty(DescriptionDisplayNameModel)?.name
                "<li><a href='${url}'>${displayName}</a></li>"
            }.join('\n                ')
        if (listItems == "") {
            return ""
        }
        String result = """<h3>${header}</h3>
        <p>
            <ul>
                ${listItems}
            </ul>
        </p>"""
        return result
    }
}
