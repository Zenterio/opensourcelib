package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator;
import com.zenterio.jenkins.models.ModelProperty;
import com.zenterio.jenkins.models.job.JobShellStepModel;


class JobShellStepGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobShellStepModel m = (JobShellStepModel) model
        entity.with {
                steps {
                    shell(m.getScript())
                }
        }
    }
}
