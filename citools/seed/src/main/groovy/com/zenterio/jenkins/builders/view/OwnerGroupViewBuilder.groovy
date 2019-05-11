package com.zenterio.jenkins.builders.view

import com.zenterio.jenkins.configuration.Owner
import com.zenterio.jenkins.configuration.ContactInformationCollection
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.view.*
import com.zenterio.jenkins.models.common.DescriptionModel
import com.zenterio.jenkins.models.display.DescriptionDisplayModel

class OwnerGroupViewBuilder implements IModelBuilder {

    private String group
    private ContactInformationCollection owners
    private List<String> jobNames

    public OwnerGroupViewBuilder(String group) {
        this.group = group
        this.owners = []
        this.jobNames = []
    }

    public addJob(String displayName) {
        if (!this.jobNames.contains(displayName)) {
            this.jobNames.add(displayName)
        }
    }

    public addOwner(Owner owner) {
        if (!this.owners.contains(owner)) {
            this.owners.add(owner)
        }
    }

    @Override
    public IModel build() {
        ModelEntity view = new ViewModel();
        view << new ViewNameModel(this.group)
        view << new ViewJobSelectionModel("", this.jobNames)
        IModel desc = new DescriptionModel("")
        view << desc << new DescriptionDisplayModel("Test jobs in owner-group ${this.group}${desc.renderOwnersHtml(this.owners)}")
        view << new ViewColumnsModel()
        return view
    }
}