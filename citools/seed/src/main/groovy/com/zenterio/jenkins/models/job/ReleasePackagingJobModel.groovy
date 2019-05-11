package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.ReleasePackaging
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.scriptlet.FileScriptlet
import com.zenterio.jenkins.postbuild.ReleasePackagingScriptlet

class ReleasePackagingJobModel extends JobModel{

    protected Origin origin
    protected String scriptletsDirectory
    protected ReleasePackaging releasePackaging

    /**
     * Reference to the release package post build action property model
     * added to the parent so that exact same property can be removed if
     * the parent is unset.
     */
    protected IModel releasePackagingAction

    /**
     * The job name of the job that should be release-packaged.
     */
    protected String jobNameToReleasePackage

    public ReleasePackagingJobModel(String scriptletDirectory, ReleasePackaging releasePackaging, Origin origin) {
        super()
        this.origin = origin
        this.releasePackaging = releasePackaging
        this.releasePackagingAction = null
        this.scriptletsDirectory = scriptletDirectory
        this.jobNameToReleasePackage = null
    }

    /**
     * Event handler for setParent
     * The parent is assigned a new property to interact with the
     * release packaging job.
     *
     * @param parent the new parent
     */
    @Override
    protected void onSetParent(IModel parent) {
        String releasePackagingJobName = this.getChild(JobNameModel)?.name
        parent << new JobGroovyPostBuildModel(
            new ReleasePackagingScriptlet(
                    new FileScriptlet("${this.scriptletsDirectory}/ReleasePackagingSummaryAction.groovy"),
                       releasePackagingJobName,
                       this.releasePackaging.configurable,
                       this.origin))
        this.jobNameToReleasePackage = parent.getChild(JobNameModel)?.name
    }

    /**
     * Event handler for unsetParent
     * The the release-packaging-property added on onSetParent is removed from the oldParent.
     */
    @Override
    protected void onUnsetParent(IModel oldParent) {
        oldParent.removeChild(this.releasePackagingAction)
        this.jobNameToReleasePackage = null
    }

    public String getJobNameToReleasePackage() {
        return this.jobNameToReleasePackage
    }

}
