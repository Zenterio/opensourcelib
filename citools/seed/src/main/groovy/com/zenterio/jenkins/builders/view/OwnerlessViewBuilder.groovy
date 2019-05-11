package com.zenterio.jenkins.builders.view

import com.zenterio.jenkins.configuration.Owner
import com.zenterio.jenkins.configuration.ContactInformationCollection
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.view.*
import com.zenterio.jenkins.models.common.DescriptionModel
import com.zenterio.jenkins.models.display.DescriptionDisplayModel

class OwnerlessViewBuilder implements IModelBuilder {

    private String group
    private ContactInformationCollection owners
    private List<String> jobNames

    public OwnerlessViewBuilder() {
        this.jobNames = []
    }

    public addJob(String displayName) {
        if (!this.jobNames.contains(displayName)) {
            this.jobNames.add(displayName)
        }
    }

    @Override
    public IModel build() {
        ModelEntity view = new ViewModel();
        view << new ViewNameModel("ownerless")
        view << new ViewJobSelectionModel("", this.jobNames)
        IModel desc = new DescriptionModel("")
        view << desc << new DescriptionDisplayModel("Test jobs not owned by anyone.")
        view << new ViewColumnsModel()
        return view
    }
}
