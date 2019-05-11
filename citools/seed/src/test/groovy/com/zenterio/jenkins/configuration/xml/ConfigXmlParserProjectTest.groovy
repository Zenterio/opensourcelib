package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.*

class ConfigXmlParserProjectTest extends ConfigXmlParserTestCase {

    protected void setUp() {
        super.setUp("project")
    }

    void testParseProjectAttributes() {
        String xml = """<project name="NAME"/>"""
        Project result = this.parse(xml, false)
        assert result.name == "NAME"
    }

    void testParseMultipleOrigins() {
        String xml = """\
<project name="P">
    <origin />
    <origin />
</project>
"""
        Project result = this.parse(xml, false)
        assert result.origins.size() == 2
    }

    void testParseMaximalProject() {
        String xml = """\
<project name="projname">
    <origin name="o">
        <repository name="repo" dir="dir" remote="remote" branch="b" />
        <product name="p"/>
    </origin>
</project>
"""
        Project result = this.parse(xml)
        assert result.origins.size() == 1
    }
}
