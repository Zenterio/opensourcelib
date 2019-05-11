package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Product

class ConfigXmlParserProductTest extends ConfigXmlParserTestCase
{

    protected void setUp() {
        super.setUp("product")
    }

    void testParseProductAttributes() {
        def xml = """<product name="NAME"/>"""
        Product result = this.parse(xml)
        assert result.name == "NAME"
    }

    void testAltNameDefaultsToName() {
        def xml = """<product name="NAME"/>"""
        Product result = this.parse(xml)
        assert result.altName == "NAME"
    }

    void testParseMaximalProduct(){
        def xml = """\
<product name="projname" alt-name="altname">
    <build-flow />
    <cache />
    <coverity />
    <csv-data-plot />
    <csv-data-plot />
    <doc />
    <inc-build-flow />
    <sw-upgrade offset="10"/>
    <sw-upgrade offset="3"/>
    <build-env enabled="true" env="my_env"/>
    <build-node label="NODE-LABEL1" />
    <build-node label="NODE-LABEL2" />
    <build-timeout policy="absolute" minutes="5" />
    <credential enabled="false"/>
    <credential enabled="false"/>
    <custom-build-step />
    <custom-build-step />
    <description>DESC</description>
    <incremental/>
    <log-parsing config="path/to/config.yaml"/>
    <make-prefix value="makeprefix"/>
    <make-root name="makeroot"/>
    <make-target name="maketarget"/>
    <resources label="a"/>
    <techlead name="tech lead" email="tl@mail"/>
    <variable name="var-name">var-value</variable>
    <watcher name ="watcher" email="watcher@example.com" />
    <watcher name ="second watcher" email="second.watcher@example.com" />
    <debug />
    <release />
    <production />
    <unit-test />
</product>
"""
        Product result = this.parse(xml)
        assert result.name == "projname"
        assert result.altName == "altname"
        assert result.coverity.enabled == true
        assert result.csvDataPlots.size() == 2
        assert result.doc.enabled == true
        assert result.swUpgrades.size() == 2
        assert result.swUpgrades[0].offset == 10
        assert result.swUpgrades[1].offset == 3
        assert result.unitTest.enabled == true
        assert result.buildEnv.env == "my_env"
        assert result.buildNodes.size() == 2
        assert result.buildTimeout.minutes == 5
        assert result.cache.ccacheEnabled == true
        assert result.credentials.size() == 2
        assert result.customBuildSteps.size() == 2
        assert result.description.description == "DESC"
        assert result.incremental.enabled == true
        assert result.logParsing.configurationFile == "path/to/config.yaml"
        assert result.makePrefix.value == "makeprefix"
        assert result.makeRoot.name == "makeroot"
        assert result.makeTarget.name == "maketarget"
        assert result.resources.enabled == true
        assert result.techLead.name == "tech lead"
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
        assert result.debug.enabled == true
        assert result.release.enabled == true
        assert result.production.enabled == true
    }
}
