package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Repository

class ConfigXmlParserRepositoryTest extends GroovyTestCase
{
    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    private Object parse(String xml) {
        return this.parser.parse(this.xp.parseText(xml))
    }

    void testParseRequiredRepository() {
        def xml = """\
        <repository name="repo"
                    dir="dir"
                    remote="remote"
                    branch="branch"
                    />
        """
        Repository result = parse(xml)
        assert result.name == "repo"
        assert result.directory == "dir"
        assert result.remote == "remote"
        assert result.branch == "branch"
        assert result.configurable == null
    }

    void testParsConfigurableRepository() {
        def xml = """\
        <repository name="repo"
                    dir="dir"
                    remote="remote"
                    branch="branch"
                    configurable="true"
                    />
        """
        Repository result = parse(xml)
        assert result.configurable == true
    }
}
