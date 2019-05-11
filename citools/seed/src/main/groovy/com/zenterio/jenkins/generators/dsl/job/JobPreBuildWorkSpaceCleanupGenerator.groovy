package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobPreBuildWorkspaceCleanupModel

class JobPreBuildWorkSpaceCleanupGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobPreBuildWorkspaceCleanupModel m = (JobPreBuildWorkspaceCleanupModel) model
        entity.with {
            wrappers {
                preBuildCleanup {
                    if (m.excludePattern) {
                        excludePattern(m.excludePattern)
                        deleteDirectories(true)
                    } else {
                        includePattern("*")
                        deleteDirectories(true)
                    }
                }
            }
        }
    }
}
