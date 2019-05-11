package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.configuration.Variable
import com.zenterio.jenkins.configuration.VariableCollection
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.FileScriptlet
import com.zenterio.jenkins.scriptlet.FileScriptletFactory
import com.zenterio.jenkins.scriptlet.StringScriptlet

import static com.zenterio.jenkins.scriptlet.Token.tokenizeAndEscape

/**
 * This class are used to construct build step scriptlets based on the
 * constructor/factory closure passed to it via the constructor.
 * The class assumes that a sub-folder named buildsteps exist inside
 * the root scriptlet directory specified via the constructor.
 */
class BuildStepFactory {

    final private FileScriptletFactory factory
    final private Closure constructor
    final private VariableCollection variableCollection

    /**
     *
     * @param scriptletDirectory    The path to the scriptlet root directory.
     *                              The factory assumes that a sub-folder named
     *                              buildsteps exists in this path.
     * @param constructor           A closure that takes two arguments, a IScriptlet,
     *                              and swUpgradeOffset. The closure returns an instance of
     *                              BaseBuildStepScriptlet or a sub-class thereof.
     */
    public BuildStepFactory(String scriptletDirectory, VariableCollection variableCollection, Closure constructor) {
        this.variableCollection = variableCollection
        this.constructor = constructor
        this.factory = new FileScriptletFactory("${scriptletDirectory}/buildsteps")
    }

    /**
     *
     * @param path  Fully qualified path to the scriptlet file.
     * @param swUpgradeOffset SW upgrade offset
     * @return build step scriptlet
     */
    public BaseBuildStepScriptlet fromFile(String path, int swUpgradeOffset) {
        BaseBuildStepScriptlet result = this.fromTemplate(path, swUpgradeOffset)
        return result
    }

    /**
     *
     * @param name  Build step name. The name must be matched by a file with
     *              the same name in the buildstep directory inside the scriptlet
     *              root directory
     * @param swUpgradeOffset SW upgrade offset
     * @return      build step scriptlet
     */
    public BaseBuildStepScriptlet fromName(String name, int swUpgradeOffset) {
        BaseBuildStepScriptlet result = this.fromTemplate(this.factory.fromFile("${name}"), swUpgradeOffset)
        return result
    }


    /**
     *
     * @param code  The raw unexpanded code as a string
     * @param swUpgradeOffset SW upgrade offset
     * @return build step scriptlet
     */
    public BaseBuildStepScriptlet fromString(String code, int swUpgradeOffset) {
        BaseBuildStepScriptlet result = this.fromTemplate(new StringScriptlet(code), swUpgradeOffset)
        return result
    }

    /**
     *
     * @param template  A template scriptlet used to construct the build step
     * @param swUpgradeOffset SW upgrade offset
     * @return build step scriptlet
     */
    public BaseBuildStepScriptlet fromTemplate(IScriptlet template, int swUpgradeOffset) {
        BaseBuildStepScriptlet result = this.constructor(template, swUpgradeOffset)

        variableCollection.each { Variable variable ->
            result.addMacroDefinitions(tokenizeAndEscape(variable.name, variable.value))
        }

        return result
    }

}
