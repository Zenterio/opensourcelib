package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.FileScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token

class BuildInfoBuildStepScriptlet extends BuildStepScriptlet {

    public BuildInfoBuildStepScriptlet(String scriptletDirectory,
                                       String productName,
                                       String originName,
                                       Repository[] repositories) {
        super(new FileScriptlet(scriptletDirectory,"build-info"), productName, 0)

        StringBuilder repositoryDescriptionBuilder = new StringBuilder()

        // Unroll the repositories description
        repositoryDescriptionBuilder << repositories.collect({ repository ->
            """echo -------------------------------------------------
echo "Repository: ${repository.name}"
echo "Remote: ${repository.remote}"
echo "Branch: ${repository.branch}"
cd "\${WORKSPACE}/${repository.directory}"
echo "Commit: \$(git rev-parse HEAD)"
echo "Directory: ${repository.directory}"
echo "Message:"
git log -1 --pretty=%B
"""
                }).join()
        this.addMacroDefinitions([(token('ORIGIN_NAME')): escape(originName)])
        this.addMacroDefinitions([(token('REPOSITORIES_DESCRIPTIONS')): escape(repositoryDescriptionBuilder.toString())])
    }
}
