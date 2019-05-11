package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobArtifactModel

class JobArtifactGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobArtifactModel m = (JobArtifactModel) model
        entity.with {
            publishers {
                archiveArtifacts {
                    allowEmpty(true)
                    pattern(m.getPattern())
                    fingerprint(m.fingerprinting)
                }
            }
        }
    }
}
