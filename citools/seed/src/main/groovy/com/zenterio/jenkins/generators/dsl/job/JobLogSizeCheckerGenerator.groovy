package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator;
import com.zenterio.jenkins.models.ModelProperty;
import com.zenterio.jenkins.models.job.JobLogSizeCheckerModel;


class JobLogSizeCheckerGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobLogSizeCheckerModel m = (JobLogSizeCheckerModel) model;
        entity.with {
            wrappers {
                logSizeChecker {
                    maxSize(m.maxSize)
                    failBuild(m.failBuild)
                }
            }
        }
    }
}
