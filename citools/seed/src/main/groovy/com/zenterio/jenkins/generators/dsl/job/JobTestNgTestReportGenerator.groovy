package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobJUnitTestReportModel
import com.zenterio.jenkins.models.job.JobTestNgTestReportModel

class JobTestNgTestReportGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobTestNgTestReportModel m = (JobTestNgTestReportModel) model
        entity.with {
            publishers {
                archiveTestNG(m.includePattern) {
                    showFailedBuildsInTrendGraph(true)
                    markBuildAsUnstableOnSkippedTests(false)
                }
            }
        }
    }
}
