package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobJUnitTestReportModel extends ModelProperty {

    final String includePattern

    public JobJUnitTestReportModel(String includePattern) {
        super()
        this.includePattern = includePattern
    }

    public String getIncludePattern() {
        return this.includePattern
    }
}
