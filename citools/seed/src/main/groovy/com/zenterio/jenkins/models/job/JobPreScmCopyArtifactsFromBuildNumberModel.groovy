package com.zenterio.jenkins.models.job

import groovy.transform.InheritConstructors

/**
 * Copies artifacts from a given build based on build-number, before scm steps are taken.
 */
@InheritConstructors
class JobPreScmCopyArtifactsFromBuildNumberModel extends JobCopyArtifactsFromBuildNumberModel {
}
