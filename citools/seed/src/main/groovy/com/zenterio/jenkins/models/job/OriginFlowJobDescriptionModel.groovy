package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.display.DescriptionDisplayNameModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.common.UrlModel
import com.zenterio.jenkins.configuration.*


class OriginFlowJobDescriptionModel extends JobDescriptionModel {

    ProjectManager projectManager
    TechLead techLead
    ContactInformationCollection watchers

    public OriginFlowJobDescriptionModel(ProjectManager projectManager,
        TechLead techLead, ContactInformationCollection watchers) {
        super("");
        this.projectManager = projectManager;
        this.techLead = techLead;
        this.watchers = watchers;
    }

    public String getDescription() {
        IModel entity = this.getParent(ModelEntity, false)
        String productList =
            entity.getChildren(ProductFlowJobModel, false, true).collect {
                    ProductFlowJobModel productFlow ->
                String url = productFlow.getProperty(UrlModel, false, true)?.url
                String displayName = productFlow.getProperty(DescriptionDisplayNameModel, false, true)?.name
                "<li><a href='${url}'>${displayName}</a></li>"
            }.join('\n                ')

        String desc = """
<div style='position: relative; float: left; min-width: 40%; margin: 15px; border: 1px solid #bbbbbb; padding: 5px 5px; background: #f0f0f0; border-radius:10px; box-shadow: 5px 5px 5px #888888;'>
    <div style='position: relative; min-width: 40%; float: left; margin: 5px; padding: 5px 10px;'>
        <h3>Products</h3>
        <p>
            <ul>
                ${productList}
            </ul>
        </p>
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
}
