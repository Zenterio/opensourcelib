package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.BuildEnv

class ConfigXmlParserBuildEnvTest extends ConfigXmlParserTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        super.setUp("build-env")
    }

    public void testEnabledBuildEnv() {
        def xml = """<build-env enabled="true"/>"""
        BuildEnv build_env = this.parse(xml)
        assert build_env.enabled == true
    }

    public void testDisabledBuildEnv() {
        def xml = """<build-env enabled="false"/>"""
        BuildEnv build_env = this.parse(xml)
        assert build_env.enabled == false
    }

    public void testBuildEnvDefault() {
        def xml = """<build-env/>"""
        BuildEnv build_env = this.parse(xml)
        assert build_env.enabled == true
    }

    public void testBuildEnvImage() {
        def xml = """<build-env enabled="true" env="my_image.u15"/>"""
        BuildEnv build_env = this.parse(xml)
        assert build_env.env == "my_image.u15"
    }

    public void testBuildEnvArgs() {
        def xml = """<build-env enabled="true" args="--some-arg value"/>"""
        BuildEnv build_env = this.parse(xml)
        assert build_env.args == "--some-arg value"
    }
}
