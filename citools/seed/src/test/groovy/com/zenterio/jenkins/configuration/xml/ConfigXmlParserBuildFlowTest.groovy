package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.BuildFlow
import com.zenterio.jenkins.configuration.BuildFlowStyle

class ConfigXmlParserBuildFlowTest extends ConfigXmlParserTestCase {

    protected void setUp() {
        super.setUp("build-flow")
    }

    public void testStyleToString() {
        assert "${BuildFlowStyle.ZIDS_UNIT_TEST_PARALLEL}" == "zids-unit-test-parallel"
    }

    public void testStyles() {
        for (BuildFlowStyle style: BuildFlowStyle.values()) {
            String xml = """<build-flow style="${style}"/>"""
            BuildFlow result = this.parse(xml)
            assert result.style == style
        }
    }

    public void testDefaultAttributes() {
        String xml = """<build-flow />"""
        BuildFlow result = this.parse(xml)
        assert result.style == BuildFlowStyle.ZIDS_UNIT_TEST_SERIAL
    }

    public void testIncBuildFlowDefault() {
        super.setUp("inc-build-flow")
        String xml = """<inc-build-flow/>"""
        BuildFlow result = this.parse(xml)
        assert result.style == BuildFlowStyle.ZIDS_UNIT_TEST_PARALLEL
    }
}
