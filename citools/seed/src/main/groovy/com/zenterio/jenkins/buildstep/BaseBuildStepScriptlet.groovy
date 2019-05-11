package com.zenterio.jenkins.buildstep
/*
 *TODO: The scope of build-scripts have grown so it is no longer realistic to collect documentation and definition of all build-script macros in the same base class.
 * We need to split the base class in multiple levels to group them by use.
 * ZMT-2047
 */

import static com.zenterio.jenkins.scriptlet.Token.tokenizeAndEscape

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

/**
 *
 * <strong>Macros available:</strong>
 * <p>
 * <dl>
 * <dt>${ARTIFACTS_DIR}</dt>
 * <dd>relative path to the directory where artifacts are collected.</dd>
 * <dt>${ARTIFACTS_PATH}</dt>
 * <dd>the full path to the directory where artifacts are collected.</dd>
 * <dt>${PROJECT}</dt>
 * <dd>Jenkins Seed project name</dd>
 * <dt>${ORIGIN}</dt>
 * <dd>Jenkins Seed origin name</dd>
 * <dt>${PRODUCT}</dt>
 * <dd>ZiDS product name (e.g. ZHT2104)</dd>
 * <dt>${PRODUCT_ALT_NAME}</dt>
 * <dd>ZiDS product alternative name</dd>
 * <dt>${BUILD_TYPE}</dt>
 * <dd>Build type (debug, production or release)</dd>
 * <dt>${BUILD_TYPE_OPT}</dt>
 * <dd>ZiDS make file flag for this type of bild (e.g. "ZSYS_RELEASE=y")</dd>
 * <dt>${JOB_TYPE}</dt>
 * <dd>Job type (e.g. "incremental, compile, coverity, ...")</dd>
 * <dt>${CONFIGURATION_FILE}</dt>
 * <dd>For scripts that run a tool that take a configuration file argument, full path.</dt>
 * <dt>${COVERAGE_REPORT_XML} </dt>
 * <dd>Argument to ZiDS build system that generate a coverage report.</dd>
 * <dt>${BUILD_ENVIRONMENT}</dt>
 * <dd>Prefixes the MAKE_PREFIX and the complete make command to be able to run inside a build environment such as Docker (using Zebra)</dd>
 * <dt>${MAKE}</dt>
 * <dd>make binary, full path</dd>
 *  <dt>${MAKE_PREFIX}</dt>
 * <dd>Prefix to the make command, a environmental variable declaration or call to other command (e.g. "VAR=value")</dd>
 * <dt>${MAKE_ROOT}</dt>
 * <dd>ZiDS source root relative workspace (e.g. "zids")</dd>
 * <dt>${MAKE_TARGET}</dt>
 * <dd>ZiDS make target (e.g. "bootimage")</dd>
 * <dt>${ZBLD_DIR_DL}</dt>
 * <dd>ZiDS download directory</dd>
 * <dt>${COMPILATION_CONFIG_PATH}</dt>
 * <dd>Path to configuration.mk file</dd>
 * <dt>${COVERITY_STREAM}</dt>
 * <dd>Name of the coverity stream that the analysis will be committed to</dd>
 * <dt>${COVERITY_WORK_DIR}</dt>
 * <dd>The directory where coverity will store intermediate data and temp-files during execution.</dd>
 * <dt>${COVERITY_BUILD}</dt>
 * <dd>Coverity build command to prepend make command when building the product</dd>
 * <dt>${COVERITY_ANALYSIS}</dt>
 * <dd>Command to run coverity analysis</dd>
 * <dt>${COVERITY_EXPORT_CVA}</dt>
 * <dd>Command to export CVA file</dd>
 * <dt>${COVERITY_CVA_FILE}</dt>
 * <dd>path to where CVA file is exported</dd>
 * <dt>${COVERITY_COMMIT}</dt>
 * <dd>Commit the Coverity analysis</dd>
 * <dt>${ORIGIN_INFO}</dt>
 * <dd>Code to generate information about origins for build-info</dd>
 * <dt>${PRODUCT_CONFIGURATION}</dt>
 * <dd>Product configuration file for Kazam</dd>
 * <dt>${BOX_CONFIGURATION}</dt>
 * <dd>STB configuration file for Kazam</dd>
 * <dt>${SOURCE_DIR}</dt>
 * <dd>Directory where artifacts needed for flashing can be found</dd>
 * <dt>${SW_UPGRADE_ARGUMENTS}</dt>
 * <dd>The arguments used to change ZSYS_SW_UPGRADE_VERSION. This is either empty or the assignment "ZSYS_SW_UPGRADE_VERSION=${ZSYS_SW_UPGRADE_VERSION}".</dd>
 * <dt>${SW_UPGRADE_CALCULATION}</dt>
 * <dd>The code to calculate a new ZSYS_SW_UPGRADE_VERSION.</dd>
 * <dt>${SW_UPGRADE_OFFSET}</dt>
 * <dd>The SW upgrade offset value".</dd>
 * <dt>${SW_UPGRADE_OFFSET_DIR}</dt>
 * <dd>Sub directory for artifacts when using sw upgrade offset, starts with /.</dd>
 * <dt>${TEST_ROOT}</dt>
 * <dd>Kazam test root</dd>
 * <dt>${EXTRA_ARGUMENTS}</dt>
 * <dd>Extra arguments for a build step command.</dd>
 * <dt>${CCACHE_DIR}</dt>
 * <dd>The directory that will be used for the ccache cache.</dd>
 * <dt>${CCACHE_ARGUMENT}</dt>
 * <dd>The ABS argument to activate ccache. Should be ZBLD_CCACHE=y to activate ccache and empty otherwise.</dd>
 * <dt>${CCACHE_PUBLISH}</dt>
 * <dd>Expands to the string "yes" if the ccache should be published, otherwise empty string.</dd>
 * <dt>${CCACHE_SIZE}</dt>
 * <dd>The size of the ccache including its unit.</dd>
 * <dt>${CCACHE_STORAGE}</dt>
 * <dd>The path where the ccache is stored inbetween builds.</dd>
 * <dt>${UNITTEST_ARGUMENT}</dt>
 * <dd>The ABS argument to activate/deactivate unit testing</dd>
 * </dl>
 * <p>
 * <strong>Examples of use:</strong>
<code><pre><blockquote>
&lt;custom-build-step&gt;
${COVERITY_BUILD} ${MAKE} ${BUILD_TYPE_OPT} ZSYS_PRODUCT=${PRODUCT} ${MAKE_TARGET}
cp build/${PRODUCT}/${BUILD_TYPE}/images/kfs.zmg ${ARTIFACTS_PATH}
${COVERITY_ANALYSIS}
${COVERITY_COMMIT}
&lt;/custom-build-step&gt;
</blockquote></pre></code>
 * <p>
 * <strong>Development Notes</strong>
 * When defining macros used in jenkins seed, create them using the Token class
 * as the example below; notice the use of parenthesis around the token() call.
 * <p>
 * Further, text containing regex magic markers that are not intended to be used
 * as such must be escaped using Token.escape.
<code><pre><blockquote>
import static com.zenterio.jenkins.scriptlet.Token.token
import static com.zenterio.jenkins.scriptlet.Token.escape

class MyScriptlet extends BaseBuildStepScriptlet {
    public MyScriptlet(IScriptlet template) {
        super(template)
        this.addMacroDefinitions([(token('CURRENCY')): escape('US$')])
    }
}
</blockquote></pre></code>
 */

class BaseBuildStepScriptlet extends TemplateScriptlet {

    public BaseBuildStepScriptlet(IScriptlet template) {
        super(template)

        /*
         * All macros supported by build-step.
         * Any new macros should also be added here to create
         * the default behavior of expanding them to empty string.
         * All macros are documented in the doc-section of this class.
         */
        this.addMacroDefinitions(tokenizeAndEscape('ARTIFACTS_DIR', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ARTIFACTS_PATH', ''))
        this.addMacroDefinitions(tokenizeAndEscape('PROJECT', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ORIGIN', ''))
        this.addMacroDefinitions(tokenizeAndEscape('PRODUCT', ''))
        this.addMacroDefinitions(tokenizeAndEscape('PRODUCT_ALT_NAME', ''))
        this.addMacroDefinitions(tokenizeAndEscape('BUILD_TYPE', ''))
        this.addMacroDefinitions(tokenizeAndEscape('BUILD_TYPE_OPT', ''))
        this.addMacroDefinitions(tokenizeAndEscape('JOB_TYPE', ''))
        this.addMacroDefinitions(tokenizeAndEscape('CONFIGURATION_FILE', ''))
        this.addMacroDefinitions(tokenizeAndEscape('COVERAGE_REPORT_XML', ''))
        this.addMacroDefinitions(tokenizeAndEscape('BUILD_ENVIRONMENT', ''))
        this.addMacroDefinitions(tokenizeAndEscape('BUILD_ENVIRONMENT_PREFIX', ''))
        this.addMacroDefinitions(tokenizeAndEscape('MAKE', ''))
        this.addMacroDefinitions(tokenizeAndEscape('MAKE_PREFIX', ''))
        this.addMacroDefinitions(tokenizeAndEscape('MAKE_ROOT', ''))
        this.addMacroDefinitions(tokenizeAndEscape('MAKE_TARGET', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ZBLD_DIR_DL', ''))
        this.addMacroDefinitions(tokenizeAndEscape('COMPILATION_CONFIG_PATH', ''))
        this.addMacroDefinitions(tokenizeAndEscape('COVERITY_STREAM', ''))
        this.addMacroDefinitions(tokenizeAndEscape('COVERITY_WORK_DIR', ''))
        this.addMacroDefinitions(tokenizeAndEscape('COVERITY_BUILD', ''))
        this.addMacroDefinitions(tokenizeAndEscape('COVERITY_ANALYSIS', ''))
        this.addMacroDefinitions(tokenizeAndEscape('COVERITY_CVA_FILE', ''))
        this.addMacroDefinitions(tokenizeAndEscape('COVERITY_EXPORT_CVA', ''))
        this.addMacroDefinitions(tokenizeAndEscape('COVERITY_COMMIT', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ORIGIN_INFO', ''))
        this.addMacroDefinitions(tokenizeAndEscape('EXTRA_ARGUMENTS', ''))
        this.addMacroDefinitions(tokenizeAndEscape('K2_SCRIPTLET_PREFIX', ''))
        this.addMacroDefinitions(tokenizeAndEscape('K2_COMMAND', ''))
        this.addMacroDefinitions(tokenizeAndEscape('K2_COMMAND_ARGUMENTS', ''))
        this.addMacroDefinitions(tokenizeAndEscape('K2_TIMEOUT', ''))
        this.addMacroDefinitions(tokenizeAndEscape('PRODUCT_CONFIGURATION', ''))
        this.addMacroDefinitions(tokenizeAndEscape('BOX_CONFIGURATION', ''))
        this.addMacroDefinitions(tokenizeAndEscape('SOURCE_DIR', ''))
        this.addMacroDefinitions(tokenizeAndEscape('SW_UPGRADE_OFFSET', ''))
        this.addMacroDefinitions(tokenizeAndEscape('SW_UPGRADE_ARGUMENTS', ''))
        this.addMacroDefinitions(tokenizeAndEscape('SW_UPGRADE_CALCULATION', ''))
        this.addMacroDefinitions(tokenizeAndEscape('SW_UPGRADE_OFFSET_DIR', ''))
        this.addMacroDefinitions(tokenizeAndEscape('TEST_ROOT', ''))
        this.addMacroDefinitions(tokenizeAndEscape('CCACHE_DIR', ''))
        this.addMacroDefinitions(tokenizeAndEscape('CCACHE_ARGUMENT', ''))
        this.addMacroDefinitions(tokenizeAndEscape('CCACHE_PUBLISH', ''))
        this.addMacroDefinitions(tokenizeAndEscape('CCACHE_SIZE', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ABS_ZIDS_OUI', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ABS_ZIDS_SWVER', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ABS_ZIDS_VERSION', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ABS_ZIDS_PRODUCT_ID', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ABS_ZSYS_VERSION', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ABS_ZBLD_VERSION', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ZSYS_AUTOMATED_TEST_LOGGING', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ZBLD_MCACHE', ''))
        this.addMacroDefinitions(tokenizeAndEscape('ZBLD_IMAGE.unstripped_copy', ''))

    }
}
