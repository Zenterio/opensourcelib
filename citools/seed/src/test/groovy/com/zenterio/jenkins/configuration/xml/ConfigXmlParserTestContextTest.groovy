package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.CredentialType
import com.zenterio.jenkins.configuration.TestContext
import com.zenterio.jenkins.configuration.Upstream

class ConfigXmlParserTestContextTest extends GroovyTestCase
{
    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    private TestContext parse(String xml) {
        def parsedXml = this.xp.parseText(xml)
        return this.parser.parse(parsedXml)
    }

    void testParseMinimalTestContext() {
        String xml="""
<test-context name="NAME" >
<test-suite path="TS_PATH"/>
</test-context>
"""
        TestContext result = this.parse(xml)
        assert result.name =="NAME"
        assert result.credentials.size() == 0
        assert result.coredumpHandling == null
        assert result.epgs.length == 0
        assert result.enabled == true
        assert result.image == null
        assert result.logParsing == null
        assert result.periodic == null
        assert result.polling == null
        assert result.repositories.length == 0
        assert result.testSuites.length == 1
        assert result.upstream == Upstream.TRUE
        assert result.watchers.size() == 0
        assert result.testCommandArgs == null
        assert result.inputParameters.length == 0
        assert result.jasmine == null
        assert result.stbLabel == null
        assert result.owners.size() == 0
    }

    void testParseFullTestContext() {
        String xml="""
<test-context name="NAME" upstream="false" polling="poll" periodic="sometimes" stb-label="label" coredump-handling="false" enabled="false">
    <csv-data-plot input="data1.csv" title="Title" group="Group" scale="Y-axis" style="area" />
    <csv-data-plot input="data2.csv" title="Title" group="Group" scale="Y-axis" style="area" />
    <xml-to-csv input="data1.xml" output="data1.csv">
        <xml-data source="source.in.xml" operation="avg" field="field" caption="caption avg"/>
        <xml-data source="source.in.xml" operation="min" field="field" caption="caption min"/>
    </xml-to-csv>
    <xml-to-csv input="data2.xml" output="data2.csv">
        <xml-data source="source.in.xml" operation="max" field="field" caption="caption max"/>
    </xml-to-csv>
    <credential type="text" variable-name="TEXT_VAR_NAME" id="TEXT_ID"/>
    <credential type="file" variable-name="FILE_VAR_NAME" id="FILE_ID"/>
    <description>A description</description>
    <duration time="12:34:56"/>
    <epg path="DEFAULT_EPG"/>
    <epg path="ALTERNATE_EPG"/>
    <image artifact="kfs.zmg"/>
    <jasmine repository="repo_name" config-file="jasmine_config_file.json" disable-rcu="true" disable-rcu-check="true" url="URL"/>
    <owner name="oname" email="omail" group="ogroup"/>
    <log-parsing config="config_file.cfg"/>
    <repository name="repo" dir="dir" remote="remote" branch="branch"/>
    <resources label="a"/>
    <test-command-args value="Extra test command arguments"/>
    <test-job-input-parameter name="INPUT1" default="default1"/>
    <test-job-input-parameter name="INPUT2" default="default2"/>
    <test-suite path="TS_PATH1"/>
    <test-suite path="TS_PATH2"/>
    <test-suite path="TS_PATH3"/>
    <variable name="var-name">var-value</variable>
    <watcher name="wname" email="wmail"/>
</test-context>
"""
        TestContext result = this.parse(xml)
        assert result.name == "NAME"
        assert result.credentials.size() == 2
        assert result.credentials[0].type == CredentialType.TEXT
        assert result.credentials[0].variableName == "TEXT_VAR_NAME"
        assert result.credentials[0].id == "TEXT_ID"
        assert result.credentials[1].type == CredentialType.FILE
        assert result.credentials[1].variableName == "FILE_VAR_NAME"
        assert result.credentials[1].id == "FILE_ID"
        assert result.csvDataPlots.length == 2
        assert result.csvDataPlots[0].input == "data1.csv"
        assert result.xmlToCsvs.length == 2
        assert result.xmlToCsvs[0].input == "data1.xml"
        assert result.xmlToCsvs[0].data.length == 2
        assert result.xmlToCsvs[1].data.length == 1
        assert result.description.description == "A description"
        assert result.duration.time == "12:34:56"
        assert result.coredumpHandling == false
        assert result.epgs.length == 2
        assert result.enabled == false
        assert result.image.artifact == "kfs.zmg"
        assert result.jasmine.repository == "repo_name"
        assert result.jasmine.configFile == "jasmine_config_file.json"
        assert result.jasmine.disableRCU == true
        assert result.jasmine.disableRCUCheck == true
        assert result.jasmine.url == "URL"
        assert result.owners[0].name == "oname"
        assert result.owners[0].email == "omail"
        assert result.owners[0].group == "ogroup"
        assert result.logParsing.configurationFile == "config_file.cfg"
        assert result.periodic == "sometimes"
        assert result.polling == "poll"
        assert result.stbLabel == "label"
        assert result.resources.enabled == true
        assert result.repositories.length == 1
        assert result.repositories[0].name == "repo"
        assert result.inputParameters.length == 2
        assert result.testCommandArgs.extraArgs == "Extra test command arguments"
        assert result.testSuites.length == 3
        assert result.upstream == Upstream.FALSE
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
        assert result.watchers[0].name == "wname"
        assert result.watchers[0].email == "wmail"
    }
}
