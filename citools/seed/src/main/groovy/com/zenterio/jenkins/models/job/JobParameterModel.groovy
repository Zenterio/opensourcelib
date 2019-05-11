package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobParameterModel extends ModelProperty {

    String name
    String defaultValue
    String description

    public JobParameterModel(String name, String defaultValue,
            String description) {
        super()
        this.name = name
        this.defaultValue = defaultValue
        this.description = description
    }
}
