package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.BaseProduct
import com.zenterio.jenkins.configuration.Cache
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.scriptlet.IScriptlet

import static com.zenterio.jenkins.scriptlet.Token.tokenizeAndEscape


class IncrementalCompileBuildStepScriptlet extends CompileBuildStepScriptlet {

    public IncrementalCompileBuildStepScriptlet(IScriptlet template, JobType jobType,
                                                BuildType buildType, BaseProduct product, int swUpgradeOffset,
                                                Cache cache, boolean unittest
            ) {
        super(template, jobType, buildType, product, product.buildEnv, swUpgradeOffset,
              null, null, cache, unittest)

        this.addMacroDefinitions(tokenizeAndEscape('ZBLD_MCACHE', 'ZBLD_MCACHE=y'))
    }
}
