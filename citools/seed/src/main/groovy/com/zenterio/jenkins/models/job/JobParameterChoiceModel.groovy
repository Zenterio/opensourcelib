package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobParameterChoiceModel extends ModelProperty {

    String name
    ArrayList<String> values
    String description

    public JobParameterChoiceModel(String name, List<String> values,
            String description) {
        super()
        this.name = name
        this.values = values
        this.description = description
    }
}
