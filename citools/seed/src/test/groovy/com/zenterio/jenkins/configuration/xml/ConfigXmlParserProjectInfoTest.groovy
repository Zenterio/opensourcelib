package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.RetentionPolicyType
import com.zenterio.jenkins.configuration.*

class ConfigXmlParserProjectInfoTest extends ConfigXmlParserTestCase
{

    protected void setUp() {
        super.setUp("project-info")
    }

    void testParseProjectInfoAttributes() {
        String xml = """<project-info name="NAME"/>"""
        Project result = this.parse(xml, false)
        assert result.name == "NAME"
    }

    void testParseMaximalProjectInfo(){
        def xml = """\
<project-info name="projname">
    <build-flow />
    <cache ccache-enabled="false" />
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
    <sw-upgrade offset="7"/>
    <sw-upgrade offset="3"/>
    <trigger />
    <build-env enabled="true" args="my args" />
    <build-node label="NODE-LABEL1" />
    <build-node label="NODE-LABEL2" />
    <build-timeout policy="absolute" minutes="5" />
    <concurrent-builds />
    <credential enabled="false"/>
    <credential enabled="false"/>
    <custom-build-step />
    <custom-build-step />
    <description>DESC</description>
    <incremental/>
    <log-parsing config="path/to/config.yaml" enabled="true"/>
    <make-prefix value="makeprefix"/>
    <make-root name="makeroot"/>
    <make-target name="maketarget"/>
    <pm name="PM" email="pm@mail"/>
    <resources name="N" />
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
    <unit-test />
</project-info>
"""
        Project result = this.parse(xml)
        assert result.name == "projname"
        assert result.buildFlow.style == BuildFlowStyle.ZIDS_UNIT_TEST_SERIAL
        assert result.cache.ccacheEnabled == false
        assert result.coverity.enabled == true
        assert result.csvDataPlots.size() == 2
        assert result.doc.enabled == true
        assert result.incBuildFlow.style == BuildFlowStyle.ZIDS_UNIT_TEST_PARALLEL
        assert result.publishOverSSHList.size() == 2
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
        assert result.releasePackaging.enabled == false
        assert result.swUpgrades.size() == 2
        assert result.swUpgrades[0].offset == 7
        assert result.swUpgrades[1].offset == 3
        assert result.trigger.enabled == true
        assert result.unitTest.enabled == true
        assert result.buildEnv.args == "my args"
        assert result.buildNodes.size() == 2
        assert result.buildTimeout.minutes == 5
        assert result.cache.ccacheEnabled == false
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
        assert result.retentionPolicy.type == RetentionPolicyType.SHORT
        assert result.startedBy.enabled == true
        assert result.techLead.name == "tech lead"
        assert result.watchers.size() == 2
        assert result.workspaceBrowsing.enabled == false
    }
}
