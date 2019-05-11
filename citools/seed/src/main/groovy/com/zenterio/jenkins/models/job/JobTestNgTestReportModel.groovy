package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobTestNgTestReportModel extends ModelProperty {

    final String includePattern

    public JobTestNgTestReportModel(String includePattern) {
        super()
        this.includePattern = includePattern
    }

    public String getIncludePattern() {
        return this.includePattern
    }
}
