package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.Priority

class ConfigXmlParserOriginTest extends ConfigXmlParserTestCase
{

    protected void setUp() {
        super.setUp("origin")
    }

    void testParseOriginDefaultAttributes() {
        String xml = """<origin name="NAME" />"""
        Origin result = this.parse(xml, false)
        assert result.name == "NAME"
        assert result.configurable == false
        assert result.tagScm == true
    }

    void testParseOriginAttributes() {
        String xml = """<origin name="NAME" configurable="true" tag-scm="false" />"""
        Origin result = this.parse(xml, false)
        assert result.name == "NAME"
        assert result.configurable == true
        assert result.tagScm == false
    }

    void testParseMaximalOrigin() {
        String xml = """\
<origin name="name">
    <build-flow />
    <cache ccache-enabled="true" />
    <coverity />
    <csv-data-plot />
    <csv-data-plot />
    <doc />
    <inc-build-flow />
    <publish-build-over-ssh
        enabled="false" name="N"
        server="S"
        artifact-pattern=""
        root-dir="" />
    <publish-over-ssh server="S" enabled="false">
        <transfer-set src="src" />
    </publish-over-ssh>
    <release-packaging enabled="false"/>
    <sw-upgrade offset="3"/>
    <sw-upgrade offset="7"/>
    <trigger />
    <build-env enabled="true"/>
    <build-node label="NODE-LABEL1" />
    <build-node label="NODE-LABEL2" />
    <build-timeout policy="absolute" minutes="5" />
    <concurrent-builds enabled="true" />
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
    <pm name="PM" email="pm" />
    <priority level="high"/>
    <repository name="repo1" dir="dir" remote="remote" branch="b" />
    <repository name="repo2" dir="dir" remote="remote" branch="b" />
    <resources name="a1"/>
    <retention-policy duration="short" />
    <started-by enabled="true"/>
    <techlead name="tech lead" email="tl@mail"/>
    <variable name="var-name">var-value</variable>
    <watcher name ="watcher" email="watcher@example.com" />
    <watcher name ="second watcher" email="second.watcher@example.com" />
    <workspace-browsing enabled="false" />
    <debug />
    <release />
    <production />
    <unit-test enabled="true" />
    <product name="p1"/>
    <product name="p2"/>
</origin>
"""
        Origin result = this.parse(xml)
        assert result.name == "name"
        assert result.configurable == false
        assert result.tagScm == true
        assert result.coverity.enabled == true
        assert result.csvDataPlots.size() == 2
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
        assert result.publishOverSSHList.size() == 2
        assert result.releasePackaging.enabled == false
        assert result.swUpgrades.size() == 2
        assert result.swUpgrades[0].offset == 3
        assert result.swUpgrades[1].offset == 7
        assert result.doc.enabled == true
        assert result.trigger.enabled == true
        assert result.buildEnv.enabled == true
        assert result.buildNodes.size() == 2
        assert result.buildTimeout.minutes == 5
        assert result.cache.ccacheEnabled == true
        assert result.concurrentBuilds.enabled == true
        assert result.credentials.size() == 2
        assert result.customBuildSteps.size() == 2
        assert result.description.description == "DESC"
        assert result.incremental.enabled == true
        assert result.logParsing.configurationFile == "path/to/config.yaml"
        assert result.makePrefix.value == "makeprefix"
        assert result.makeRoot.name == "makeroot"
        assert result.makeTarget.name == "maketarget"
        assert result.pm.name == "PM"
        assert result.resources.enabled == true
        assert result.repositories.size() == 2
        assert result.startedBy.enabled == true
        assert result.techLead.email == "tl@mail"
        assert result.workspaceBrowsing.enabled == false
        assert result.watchers.size() == 2
        assert result.debug.enabled == true
        assert result.release.enabled == true
        assert result.production.enabled == true
        assert result.unitTest.enabled == true
        assert result.products.size() == 2
        assert result.priority == Priority.HIGH
    }

}
