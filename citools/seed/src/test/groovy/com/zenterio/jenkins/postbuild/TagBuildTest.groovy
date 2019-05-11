
package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.StringScriptlet

class TagBuildTest extends GroovyTestCase {

    void testTagBuild() {
        Repository[] repos = [
            new Repository("nameA", "dirA", "remote1", "branchA", false),
            new Repository("nameB", "dirB", "remote2", "branchB", false),
            new Repository("nameC", "dirC", "remote2", "branchC", false),
        ] as Repository[]

        String template = "first: #REPOSITORIES#\nsecond: #REPOSITORIES#\n#TAG-JOB-NAME#"

        TagBuildScriptlet tb = new TagBuildScriptlet(new StringScriptlet(template), repos, "tag-job-name")

        def script = tb.getContent()
        assert script == "first: nameA remote1 nameB remote2\nsecond: nameA remote1 nameB remote2\ntag-job-name";
    }
}
