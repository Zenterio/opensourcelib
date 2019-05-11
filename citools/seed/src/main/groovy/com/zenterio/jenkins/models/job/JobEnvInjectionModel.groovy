package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobEnvInjectionModel extends ModelProperty {

    Map<String,String> variables

    public JobEnvInjectionModel(Map<String,String> variables) {
        this.variables = variables
    }

}
