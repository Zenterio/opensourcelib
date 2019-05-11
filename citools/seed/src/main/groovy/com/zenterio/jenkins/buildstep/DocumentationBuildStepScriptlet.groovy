package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.MakeBuildType
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.Product
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.jobtype.JobTypeDocumentation

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token

class DocumentationBuildStepScriptlet extends CompileBuildStepScriptlet {

    public DocumentationBuildStepScriptlet(IScriptlet template,
            BuildType buildType, Product product, int swUpgradeOffset) {
        super(template, new JobTypeDocumentation(), buildType, product, product.doc.buildEnv,
            swUpgradeOffset, null, null, null, false)
        this.addMacroDefinitions([
            (token('MAKE_PREFIX')): escape(product.doc.makePrefix.value),
            (token('MAKE_ROOT')): escape(product.doc.makeRoot.name),
            (token('MAKE_TARGET')): escape(product.doc.makeTarget.name)
        ])
    }
}
