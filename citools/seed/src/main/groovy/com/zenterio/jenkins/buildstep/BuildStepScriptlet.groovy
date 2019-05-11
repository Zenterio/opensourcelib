package com.zenterio.jenkins.buildstep

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token
import static com.zenterio.jenkins.scriptlet.Token.tokenizeAndEscape

import com.zenterio.jenkins.scriptlet.IScriptlet

class BuildStepScriptlet extends BaseBuildStepScriptlet {

    public BuildStepScriptlet(IScriptlet template, String productName, int swUpgradeOffset) {
        super(template)
        String swUpgradeArguments = ''
        String swUpgradeCalc = ''
        String swUpgradeOffsetDir = ''
        if (swUpgradeOffset > 0) {
            swUpgradeArguments = 'ZSYS_SW_UPGRADE_VERSION=${ZSYS_SW_UPGRADE_VERSION}'
            swUpgradeCalc = """ZSYS_SW_UPGRADE_VERSION=\$((${swUpgradeOffset}+${absVariableMacro(productName, 'ZSYS_SW_UPGRADE_VERSION')}))"""
            swUpgradeOffsetDir = "/sw-upgrade-offset-${swUpgradeOffset}"

        }
        this.addMacroDefinitions(tokenizeAndEscape('ARTIFACTS_DIR', 'result${SW_UPGRADE_OFFSET_DIR}'))
        this.addMacroDefinitions([(token('ARTIFACTS_PATH')): escape('${WORKSPACE}/${ARTIFACTS_DIR}')])
        this.addMacroDefinitions(tokenizeAndEscape('PRODUCT', productName))
        this.addMacroDefinitions(tokenizeAndEscape("SW_UPGRADE_CALCULATION", swUpgradeCalc))
        this.addMacroDefinitions(tokenizeAndEscape("SW_UPGRADE_OFFSET_DIR", swUpgradeOffsetDir))
        this.addMacroDefinitions(tokenizeAndEscape('SW_UPGRADE_ARGUMENTS', swUpgradeArguments))
        this.addMacroDefinitions(tokenizeAndEscape('SW_UPGRADE_OFFSET', swUpgradeOffset.toString()))
        this.addMacroDefinitions([(token('ZBLD_DIR_DL')): escape('${HOME}/.zids/dl')])

        this.addMacroDefinitions([(token("ABS_ZBLD_VERSION")): escape(absVariableMacro(productName, "ZBLD_VERSION"))])
        this.addMacroDefinitions([(token("ABS_ZIDS_OUI")): escape(absVariableMacro(productName, "ZIDS_OUI"))])
        this.addMacroDefinitions([(token("ABS_ZIDS_PRODUCT_ID")): escape(absVariableMacro(productName, "ZIDS_PRODUCT_ID"))])
        this.addMacroDefinitions([(token("ABS_ZIDS_SWVER")): escape(absVariableMacro(productName, "ZIDS_SWVER"))])
        this.addMacroDefinitions([(token("ABS_ZIDS_VERSION")): escape(absVariableMacro(productName, "ZIDS_VERSION"))])
        this.addMacroDefinitions([(token("ABS_ZSYS_VERSION")): escape(absVariableMacro(productName, "ZSYS_VERSION"))])

        this.addMacroDefinitions(tokenizeAndEscape('CCACHE_DIR', "\${BUILD_SERVER_CCACHE_ROOT}/\${EXECUTOR_NUMBER}/.ccache"))
    }

    private static String absVariableMacro(String productName, String variableName) {
        return """\$(make ZSYS_PRODUCT=${productName} print_${variableName}| grep ${variableName}= | grep -o '"[^"]*"\$' | sed 's/"//g')"""
    }
}
