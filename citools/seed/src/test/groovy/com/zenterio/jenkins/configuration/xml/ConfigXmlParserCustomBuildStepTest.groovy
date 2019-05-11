package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.CustomBuildStepType
import com.zenterio.jenkins.configuration.CustomBuildStep;
import com.zenterio.jenkins.configuration.CustomBuildStepMode;
import com.zenterio.jenkins.configuration.Product;
import com.zenterio.jenkins.configuration.Project;
import com.zenterio.jenkins.configuration.Origin

class ConfigXmlParserCustomBuildStepTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseCustomBuildStepEmpty() {
        def xml = """<custom-build-step/>"""
        def parsedXml = xp.parseText(xml)
        CustomBuildStep result = this.parser.parse(parsedXml)
        assert result.code == ""
    }

    void testParseCustomBuildStepSimple() {
        def xml = """
<custom-build-step>echo "HELLO"</custom-build-step>
"""
        def parsedXml = xp.parseText(xml)
        CustomBuildStep result = this.parser.parse(parsedXml)
        assert result.code == 'echo "HELLO"'
        assert result.mode == CustomBuildStepMode.OVERRIDE
        assert result.enabled == true
        assert result.type == CustomBuildStepType.SHELL
    }

    void testParseCustomBuildStepExplicitOverride(){
        def xml = """<custom-build-step mode="override"/>"""
        def parsedXml = xp.parseText(xml)
        CustomBuildStep result = this.parser.parse(parsedXml)
        assert result.mode == CustomBuildStepMode.OVERRIDE
    }

    void testParseCustomBuildStepPrepend() {
        def xml = """<custom-build-step mode="prepend"/>"""
        def parsedXml = xp.parseText(xml)
        CustomBuildStep result = this.parser.parse(parsedXml)
        assert result.mode == CustomBuildStepMode.PREPEND
    }

    void testParseCustomBuildStepAppend() {
        def xml = """<custom-build-step mode="append" enabled="false"/>"""
        def parsedXml = xp.parseText(xml)
        CustomBuildStep result = this.parser.parse(parsedXml)
        assert result.mode == CustomBuildStepMode.APPEND
        assert result.enabled == false
    }

    void testParseCustomBuildStepWithTypeGroovy() {
        def xml = """<custom-build-step type="system-groovy"/>"""
        def parsedXml = xp.parseText(xml)
        CustomBuildStep result = this.parser.parse(parsedXml)
        assert result.type == CustomBuildStepType.SYSTEM_GROOVY
    }


    void testParseCustomBuildStepComplex() {
        def xml = """
<custom-build-step><![CDATA[echo hello > foo
cat < foo > bar
[ foo -eq bar ] && echo "HELLO"]]></custom-build-step>
"""
        def parsedXml = xp.parseText(xml)
        CustomBuildStep result = this.parser.parse(parsedXml)
        assert result.code == """\
echo hello > foo
cat < foo > bar
[ foo -eq bar ] && echo "HELLO"\
"""
    }

    void testParserCustomBuildStepInProduct() {
        def xml = "<product><custom-build-step>ProducT</custom-build-step></product>"
        def parsedXml = xp.parseText(xml)
        Product result = this.parser.parse(parsedXml)
        assert result.customBuildSteps[0].code == "ProducT"
    }

    void testParserCustomBuildStepInProject() {
        def xml = "<project><custom-build-step>Projector</custom-build-step></project>"
        def parsedXml = xp.parseText(xml)
        Project result = this.parser.parse(parsedXml)
        assert result.customBuildSteps[0].code == "Projector"
    }

    void testParserCustomBuildStepInOrigin() {
        def xml = "<origin><custom-build-step>original</custom-build-step></origin>"
        def parsedXml = xp.parseText(xml)
        Origin result = this.parser.parse(parsedXml)
        assert result.customBuildSteps[0].code == "original"
    }

    void testParserCustomBuildStepsInOrigin() {
        def xml = """
<origin>
<custom-build-step>prepare</custom-build-step>
<custom-build-step>compile</custom-build-step>
<custom-build-step>results</custom-build-step>
</origin>"""
        def parsedXml = xp.parseText(xml)
        Origin result = this.parser.parse(parsedXml)
        assert result.customBuildSteps[0].code == "prepare"
        assert result.customBuildSteps[1].code == "compile"
        assert result.customBuildSteps[2].code == "results"
    }
}


