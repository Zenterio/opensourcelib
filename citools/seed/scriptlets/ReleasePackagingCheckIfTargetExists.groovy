
/**
 * Auto-generated script from template ReleasePackagingCheckIfTargetExists.groovy
 *
 * @Summary
 * Publish the content of the workspace to an nfs-mount
 *
 * Macros:
 * publishRoot: "#PUBLISH_ROOT#"
 * publishPath: "#PUBLISH_PATH#"
 *
 */
import hudson.FilePath

{ it ->

    String publishRoot = "#PUBLISH_ROOT#"
    String publishPath = "#PUBLISH_PATH#"

    if (publishRoot == '' || publishPath == '') {
        throw new Exception("publishRoot and publishPath may not be empty strings. Please notify the jenkins (seed) administrators.")
    }

    String releasePath = "${publishRoot}/${publishPath}"

    FilePath dest = new FilePath(new File(releasePath))
    if (dest.exists()) {
        println("ERROR: Destination folder ${dest} already exists, aborting...")
        return 1
    }
}();