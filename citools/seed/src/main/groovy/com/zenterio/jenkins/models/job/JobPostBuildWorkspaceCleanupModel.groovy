package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

/**
 * Model the Work Space Cleanup plugin.
 *
 * Note that deleteDirectories really is about applying the
 * include/exclude patterns on sub directories.
 * <a href="https://github.com/jenkinsci/job-dsl-plugin/wiki/Job-reference">
 * Workspace Cleanup Publisher documentation for Job DSL</a>
 */
class JobPostBuildWorkspaceCleanupModel extends ModelProperty {
    protected String excludePattern

    JobPostBuildWorkspaceCleanupModel(String excluded=null) {
        super()
        this.excludePattern = excluded
    }
}
