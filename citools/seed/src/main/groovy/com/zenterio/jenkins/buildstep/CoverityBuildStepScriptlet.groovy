package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.Product
import com.zenterio.jenkins.configuration.Aggressiveness
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.scriptlet.IScriptlet
import static com.zenterio.jenkins.scriptlet.Token.token
import static com.zenterio.jenkins.scriptlet.Token.escape

class CoverityBuildStepScriptlet extends CompileBuildStepScriptlet {

    public CoverityBuildStepScriptlet(IScriptlet template, JobType jobType,
            BuildType buildType, Product product, String stream, Aggressiveness aggressiveness) {
        super(template, jobType, buildType, product, product.coverity.buildEnv, 0, null, null, null, true)
        this.addMacroDefinitions([
            (token('COVERITY_STREAM')): escape(stream),
            (token('COVERITY_AGGRESSIVENESS')): escape(aggressiveness.toString()),
            (token('COVERITY_WORK_DIR')): escape('${WORKSPACE}/intermediate'),
            (token('COVERITY_BUILD')): escape('/opt/cov-analysis/bin/cov-build --dir "${COVERITY_WORK_DIR}"'),
            (token('COVERITY_IMPORT_SCM')): escape('/opt/cov-analysis/bin/cov-import-scm --dir "${COVERITY_WORK_DIR}" --scm git --filename-regex "^(?!(\\\\${WORKSPACE}/${MAKE_ROOT}/build/|\\/zebra/workspace/${MAKE_ROOT}/build/|\\/usr|\\/lib|\\/opt)).*"'),
            (token('COVERITY_ANALYSIS')): escape('/opt/cov-analysis/bin/cov-analyze --dir "${COVERITY_WORK_DIR}" -s "${WORKSPACE}" --all -j "${NUM_CPUS_TO_USE}" --override-worker-limit --aggressiveness-level="${COVERITY_AGGRESSIVENESS}"'),
            (token('COVERITY_CVA_FILE')): escape('${ARTIFACTS_PATH}/zids.cva'),
            (token('COVERITY_EXPORT_CVA')): escape('/opt/cov-analysis/bin/cov-export-cva --dir "${COVERITY_WORK_DIR}" --output-file "${COVERITY_CVA_FILE}"'),
            (token('COVERITY_COMMIT')): escape('/opt/cov-analysis/bin/cov-commit-defects --dir "${COVERITY_WORK_DIR}" --stream ${COVERITY_STREAM} -c "${WORKSPACE}"/../../coverity.xml --scm git'),
            (token('ZBLD_UNITTEST_SANITIZER_ARGUMENT')): escape(' ZBLD_UNITTEST_SANITIZER=n'),
            ])
    }
}
