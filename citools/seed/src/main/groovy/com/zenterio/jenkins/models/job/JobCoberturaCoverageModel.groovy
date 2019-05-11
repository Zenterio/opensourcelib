package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobCoberturaCoverageModel extends ModelProperty {

    final String pattern

    public JobCoberturaCoverageModel(String pattern) {
        super()
        this.pattern = pattern
    }

    public String getPattern() {
        return this.pattern
    }
}
