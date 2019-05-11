package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.UnitTest

class ConfigXmlParserUnitTestTest extends ConfigXmlParserTestCase {

    @Override
    protected void setUp() {
        super.setUp("unit-test")
    }

    public void testBuiltInAndEnabledIsDefault() {
        String xml = """<unit-test/>"""
        UnitTest unitTest = this.parse(xml)
        assert unitTest.enabled == true
        assert unitTest.builtIn == true
    }

    public void testEnabled() {
        String xml = """<unit-test enabled="true"/>"""
        UnitTest unitTest = this.parse(xml)
        assert unitTest.enabled == true
    }

    public void testDisabled() {
        String xml = """<unit-test enabled="false"/>"""
        UnitTest unitTest = this.parse(xml)
        assert unitTest.enabled == false
    }

    public void testBuiltIn() {
        String xml = """<unit-test built-in="true"/>"""
        UnitTest unitTest = this.parse(xml)
        assert unitTest.builtIn == true
    }

    public void testStandAlone() {
        String xml = """<unit-test built-in="false"/>"""
        UnitTest unitTest = this.parse(xml)
        assert unitTest.builtIn == false
    }

    public void testParseFullUnitTest() {
        String xml = """\
<unit-test>
    <cache ccache-enabled="false" />
    <csv-data-plot />
    <csv-data-plot />
    <publish-over-ssh server="S" enabled="false">
        <transfer-set src="src" />
    </publish-over-ssh>
    <build-env enabled="true" />
    <build-timeout policy="absolute" minutes="5" />
    <credential enabled="false"/>
    <credential enabled="false"/>
    <custom-build-step />
    <custom-build-step />
    <description>DESC</description>
    <log-parsing config="path/to/config.yaml" enabled="true"/>
    <make-prefix value="makeprefix"/>
    <make-root name="makeroot"/>
    <make-target name="maketarget"/>
    <resources name="N" />
    <variable name="var-name">var-value</variable>
    <watcher name ="watcher" email="watcher@example.com" />
    <watcher name ="second watcher" email="second.watcher@example.com" />
    <workspace-browsing enabled="false" />
</unit-test>
"""
        UnitTest unitTest = this.parse(xml)
        assert unitTest.buildEnv.enabled == true
        assert unitTest.cache.ccacheEnabled == false
        assert unitTest.csvDataPlots.size() == 2
        assert unitTest.publishOverSSHList.size() == 1
        assert unitTest.buildTimeout.minutes == 5
        assert unitTest.credentials.size() == 2
        assert unitTest.customBuildSteps.size() == 2
        assert unitTest.description.description == "DESC"
        assert unitTest.logParsing.configurationFile == "path/to/config.yaml"
        assert unitTest.makePrefix.value == "makeprefix"
        assert unitTest.makeRoot.name == "makeroot"
        assert unitTest.makeTarget.name == "maketarget"
        assert unitTest.variables[0].name == "var-name"
        assert unitTest.variables[0].value == "var-value"
        assert unitTest.watchers.size() == 2
        assert unitTest.workspaceBrowsing.enabled == false
    }

}
