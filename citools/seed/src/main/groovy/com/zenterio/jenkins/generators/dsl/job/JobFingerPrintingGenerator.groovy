package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobFingerPrintingModel


class JobFingerPrintingGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobFingerPrintingModel m = (JobFingerPrintingModel) model
        entity.with {
            publishers {
                fingerprint(m.targets)
            }
        }
    }
}
