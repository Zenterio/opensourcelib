package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobCopyArtifactsFromBuildNumberModel


class JobCopyArtifactsFromBuildNumberGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        JobCopyArtifactsFromBuildNumberModel m = (JobCopyArtifactsFromBuildNumberModel) model
        entity.with {
            addCopyArtifacts(delegate.&steps, m)
        }
    }

    public static void addCopyArtifacts(context, JobCopyArtifactsFromBuildNumberModel m) {
        context {
            copyArtifacts(m.getJobName()) {
                includePatterns(m.includeGlob)
                targetDirectory(m.targetPath)
                flatten(m.flattenFiles)
                optional(true)
                buildSelector {
                    buildNumber(m.buildNumber)
                }
                fingerprintArtifacts(true)
            }
        }
    }
}