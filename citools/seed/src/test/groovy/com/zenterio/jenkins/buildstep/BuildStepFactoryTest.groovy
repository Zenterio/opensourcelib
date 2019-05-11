package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.configuration.Variable
import com.zenterio.jenkins.configuration.VariableCollection

import com.zenterio.jenkins.scriptlet.StringScriptlet
import com.zenterio.jenkins.scriptlet.IScriptlet

import groovy.util.GroovyTestCase


class BuildStepFactoryTest  extends GroovyTestCase {

    class StubBuildStepScriptlet extends BaseBuildStepScriptlet {
        public StubBuildStepScriptlet(IScriptlet template, int swUpgradeOffset) {
            super(new StringScriptlet('#PRODUCT#'))
            this.addMacroDefinitions(["#PRODUCT#": "foo ${swUpgradeOffset}"])
        }
    }

    BuildStepFactory factory

    protected void setUp() {
        String workspace = System.getenv("WORKSPACE")
        this.factory = new BuildStepFactory("${workspace}/seed/scriptlets", new VariableCollection(),
                                            { IScriptlet template, int swUpgradeOffset ->
                                                return new StubBuildStepScriptlet(template, swUpgradeOffset)
                                            })
    }

    void testFromName() {
        def c = this.factory.fromName("fake", 1)
        assert c.getContent() == "foo 1"
    }

    void testVariableCanOverrideMacroDefinitions() {
        String workspace = System.getenv("WORKSPACE")
        VariableCollection vc = [new Variable("PRODUCT", "bar")] as VariableCollection
        def factory = new BuildStepFactory("${workspace}/seed/scriptlets", vc,
                                            { IScriptlet template, int swUpgradeOffset ->
                                                return new StubBuildStepScriptlet(template, swUpgradeOffset)
                                            })
        def c = factory.fromName("fake", 1)
        assert c.getContent() == "bar"
    }

}
