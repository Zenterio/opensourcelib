package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobCompilerWarningsModel


class JobCompilerWarningsGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobCompilerWarningsModel m = (JobCompilerWarningsModel) model
        entity.with {
            publishers {
                warnings(['GNU C Compiler 4 (gcc)'],[:]) {
                    excludePattern m.excludePattern
                }
            }
        }
    }
}
