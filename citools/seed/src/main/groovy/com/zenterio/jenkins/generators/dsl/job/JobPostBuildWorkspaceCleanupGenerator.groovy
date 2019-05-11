package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator;
import com.zenterio.jenkins.models.ModelProperty;
import com.zenterio.jenkins.models.job.JobPostBuildWorkspaceCleanupModel;

class JobPostBuildWorkspaceCleanupGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobPostBuildWorkspaceCleanupModel m = (JobPostBuildWorkspaceCleanupModel) model
        entity.with {
            publishers {
                wsCleanup {
                    if (m.excludePattern) {
                        excludePattern(m.excludePattern)
                        deleteDirectories(true)
                    }
                    else {
                        includePattern("*")
                        deleteDirectories(true)
                    }
                }
            }
        }
    }
}
