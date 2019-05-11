package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.Resources
import com.zenterio.jenkins.models.ModelProperty


class JobResourcesModel extends ModelProperty {

    Resources resources

    public JobResourcesModel(Resources resources) {
        super();
        this.resources = resources
    }

}
