package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobJUnitTestReportModel
import static com.zenterio.jenkins.generators.dsl.NodeUtils.setNodeContent
import static com.zenterio.jenkins.generators.dsl.NodeUtils.getNode

class JobJUnitTestReportGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobJUnitTestReportModel m = (JobJUnitTestReportModel) model
        entity.with {
            publishers {
                archiveJunit(m.includePattern) {
                    allowEmptyResults(true)
                }

            }
        }
    }
}
