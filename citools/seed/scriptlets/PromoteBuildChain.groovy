/**
 * * Auto-generated script from template PromoteBuildChain.groovy
 *
 * topJobName: #TOP_JOB_NAME#
 * topBuildNumber: #TOP_BUILD_NUMBER#
 * topPromotionLevel: #PROMOTE_LEVEL#
 *
 * @Summary
 * This script promotes a build chain from the
 * top build.
 *
 * It is a system groovy script build step.
 *
 * Environment variables/job arguments used:
 * top_job_name : Name of job to propagate information from
 * top_build_number : Number of the build.
 *
 */

// Class definitions
/**
 * Mockup class for the Stapler interface
 *
 * It implements the minimal subset used by the Promoted Build Simple plugin
 * for these Stapler interfaces:
 * org.kohsuke.stapler.StaplerRequest
 * org.kohsuke.stapler.StaplerResponse
 *
 * Each mockup function show in the documentation how it is used.
 */
class StaplerMocker {
  def build
  int level

  /*
   * Create the mockup object
   * @param build A Jenkins build object
   * @param level Numerical (integer) promotion level.
   */
  public StaplerMocker(build, int level) {
    this.build = build
    this.level = level
  }

  /**
   * levelValue = Integer.parseInt(req.getParameter("level"));
   */
  public String getParameter(String ignored) {
    return this.level.toString()
  }

  /**
   * req.findAncestorObject(Job.class).checkPermission(Run.UPDATE);
   * req.findAncestorObject(Run.class).keepLog(true);
   */
  public findAncestorObject(type) {
    if (type == hudson.model.Job.class) {
      return this.build.getParent()
    } else if (type == hudson.model.Run.class) {
      return this.build
    } else {
      throw new hudson.AbortException("Unimplemented. Changes in plugin made mockup obsolete.")
    }
  }

  /**
   * Fake the page reload event for the response object.
   */
  public static forwardToPreviousPage(ignored) {
  }
}

//Function definitions

/**
 * Get the PromoteAction object for a build.
 * The function will create a promotion object and add it to the build if it does not exist,
 * which happens if the build was run before the plugin was installed.
 *
 * @param build A Jenkins build object.
 * @return      A Promoted builds simple PromoteAction object.
 */
def getPromoteAction(build) {
  def promoteActions = build.getBadgeActions().findAll{ action ->
      action instanceof hudson.plugins.promoted_builds_simple.PromoteAction
  }
  if (promoteActions.size() == 0) {
    def pa = new hudson.plugins.promoted_builds_simple.PromoteAction()
    build.addAction(pa)
    return pa
  } else if (promoteActions.size() == 1) {
    return promoteActions[0]
  } else {
    // While this normally is impossible, if it were to happen,
    // we can safely use the first action and delete the rest.
    build.replaceAction(promoteActions[0])
    return promoteActions[0]
  }
}

def doRecursion(declarer, build, int promoteLevel) {
    def downstreamBuilds = declarer.getDownStream(build)
    downstreamBuilds.each { downstreamBuild ->
        if (downstreamBuild != null) {
            setPromoteLevelAndRecurse(downstreamBuild, promoteLevel)
        }
    }
}

/**
 * Set the promotion level for a build
 *
 * param build        A Jenkins build object.
 * param promoteLevel Numeric promotion level
 */
def setPromoteLevelAndRecurse(build, int promoteLevel) {
    def promoteAction = getPromoteAction(build)
    def staplerMocker = new StaplerMocker(build, promoteLevel)

    println(build.getFullDisplayName())

    promoteAction.doIndex(staplerMocker as org.kohsuke.stapler.StaplerRequest,
             staplerMocker as org.kohsuke.stapler.StaplerResponse)

    if (jenkins.model.Jenkins.getInstance().getPlugin("build-flow-plugin") != null) {
        def declarer = new org.jenkinsci.plugins.buildgraphview.FlowDownStreamRunDeclarer()
        doRecursion(declarer, build, promoteLevel)
    }

    org.jenkinsci.plugins.buildgraphview.DownStreamRunDeclarer.all().each { declarer ->
        doRecursion(declarer, build, promoteLevel)
    }
}

def getPromotionDescription(int level) {
    if (level == 0) {
        return "None"
    }
    return hudson.model.Hudson.getInstance().getPlugin(hudson.plugins.promoted_builds_simple.PromotedBuildsSimplePlugin.class).getLevels().get(level - 1).getName()
}

// logic wrapped in closure to avoid polluting global scope
{ it ->
    String topJobName="#TOP_JOB_NAME#"
    String topBuildNumber="#TOP_BUILD_NUMBER#"

    def topJob = jenkins.model.Jenkins.instance.getJob(topJobName)
    def topBuild = topJob.getBuildByNumber(topBuildNumber.toInteger())
    def topPromoteAction = getPromoteAction(topBuild)
    int promoteLevel = "#PROMOTE_LEVEL#".toInteger()
    String promoteDescription = getPromotionDescription(promoteLevel)

    println("-----")
    println("Propagating promotion status for " + topJobName +" #"+topBuildNumber+ " to "+ promoteDescription)
    setPromoteLevelAndRecurse(topBuild, promoteLevel)
    println("-----")
}();
