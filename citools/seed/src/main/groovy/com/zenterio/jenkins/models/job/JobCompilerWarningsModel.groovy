package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobCompilerWarningsModel extends ModelProperty {

    final String excludePattern

    public JobCompilerWarningsModel(String excludePattern) {
        super()
        this.excludePattern = excludePattern
    }

    public String getExcludePattern() {
        return this.excludePattern
    }
}
