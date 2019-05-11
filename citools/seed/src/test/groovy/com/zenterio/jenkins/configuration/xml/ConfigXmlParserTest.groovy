package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.ConfigError;
import com.zenterio.jenkins.configuration.Origin;
import com.zenterio.jenkins.configuration.Product;
import com.zenterio.jenkins.configuration.Project;
import com.zenterio.jenkins.configuration.Repository;

class ConfigXmlParserTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseQuoteInAttribute() {
        def xml = """<product name="&quot;NAME&quot;"/>"""
        def parsedXml = xp.parseText(xml)
        def result = (Product)this.parser.parse(parsedXml)
        assert result.name == '"NAME"'
    }

    void testParseUnknownNodeShouldThrowConfigError() {
        def xml = """<fake-node value="foo" />"""
        def parsedXml = xp.parseText(xml)
        shouldFail ConfigError, {
            def result = this.parser.parse(parsedXml)
        }
    }

    void testParseProduct() {
        def xml = """<product name="NAME"/>"""
        def parsedXml = xp.parseText(xml)
        def result = (Product)this.parser.parse(parsedXml)
        assert result.name == "NAME"
    }

    void testParseRepository() {
        def xml = """<repository name="REPO"
        dir="DIR"
        remote="REMOTE"
        branch="BRANCH" />"""
        def parsedXml = xp.parseText(xml)
        def result = (Repository)this.parser.parse(parsedXml)
        assert result.name == "REPO"
        assert result.directory == "DIR"
        assert result.remote == "REMOTE"
        assert result.branch == "BRANCH"
    }

    void testOriginWithUnknownChildNodeShouldThrowConfigError() {
        def xml = """\
<origin name="ORIGIN">
  <fake-node value="foo" />
</origin>
"""
        def parsedXml = xp.parseText(xml)
        shouldFail ConfigError, {
            def result = this.parser.parse(parsedXml)
        }
    }

    void testMinimalOrigin() {
        def xml = """\
<origin name="ORIGIN">
  <product name="PROD"/>
  <repository name="REPO"
        dir="DIR"
        remote="REMOTE"
        branch="BRANCH" />
</origin>
"""
        def parsedXml = xp.parseText(xml)
        def result = (Origin)this.parser.parse(parsedXml)
        assert result.name == "ORIGIN"
        assert result.products.size() == 1
        assert result.watchers.size() == 0
        assert result.repositories.size() == 1
        assert result.trigger == null
    }

    void testOriginWithPeriodic() {
        def xml = """\
<origin name="ORIGIN">
  <trigger periodic="@daily"/>
  <product name="PROD"/>
  <repository name="REPO"
        dir="DIR"
        remote="REMOTE"
        branch="BRANCH" />
</origin>
"""
        def parsedXml = xp.parseText(xml)
        def result = (Origin)this.parser.parse(parsedXml)
        assert result.name == "ORIGIN"
        assert result.products.size() == 1
        assert result.watchers.size() == 0
        assert result.repositories.size() == 1
        assert result.trigger.polling == null
        assert result.trigger.periodic == "@daily"
    }

    void testOriginWithPolling() {
        def xml = """\
<origin name="ORIGIN">
  <trigger polling="@hourly"/>
  <product name="PROD"/>
  <repository name="REPO"
        dir="DIR"
        remote="REMOTE"
        branch="BRANCH" />
</origin>
"""
        def parsedXml = xp.parseText(xml)
        def result = (Origin)this.parser.parse(parsedXml)
        assert result.name == "ORIGIN"
        assert result.products.size() == 1
        assert result.watchers.size() == 0
        assert result.repositories.size() == 1
        assert result.trigger.polling == "@hourly"
        assert result.trigger.periodic == null
    }

    void testOriginWithPeriodicAndPolling() {
        def xml = """\
<origin name="ORIGIN">
 <trigger periodic="@weekly" polling="POLL"/>
  <product name="PROD"/>
  <repository name="REPO"
        dir="DIR"
        remote="REMOTE"
        branch="BRANCH" />
</origin>
"""
        def parsedXml = xp.parseText(xml)
        def result = (Origin)this.parser.parse(parsedXml)
        assert result.name == "ORIGIN"
        assert result.products.size() == 1
        assert result.watchers.size() == 0
        assert result.repositories.size() == 1
        assert result.trigger.periodic == "@weekly"
        assert result.trigger.polling == "POLL"
    }

    void testOriginWithWatcher() {
        def xml = """\
<origin name="ORIGIN">
  <product name="PROD"/>
  <watcher name="WATCHER" email="EMAIL"/>
  <repository name="REPO"
        dir="DIR"
        remote="REMOTE"
        branch="BRANCH" />
</origin>
"""
        def parsedXml = xp.parseText(xml)
        def origin = (Origin)this.parser.parse(parsedXml)
        assert origin.name == "ORIGIN"
        assert origin.products.size() == 1
        assert origin.watchers.size() == 1
        assert origin.repositories.size() == 1
    }

    void testOriginWithMultipleProducts() {
        def xml = """\
<origin name="ORIGIN">
    <repository name="REPO"
        dir="DIR"
        remote="REMOTE"
        branch="BRANCH" />
    <product name="PROD_A"/>
    <product name="PROD_B"/>
</origin>
"""
        def parsedXml = xp.parseText(xml)
        def origin = (Origin)this.parser.parse(parsedXml)
        assert origin.name == "ORIGIN"
        assert origin.products.size() == 2
        assert origin.watchers.size() == 0
        assert origin.repositories.size() == 1
        origin.products.each { prod ->
            prod.origin == origin
        }
    }

    void testOriginWithMultipleRepositories() {
        def xml = """\
<origin name="ORIGIN">
    <repository name="REPO"
        dir="DIR"
        remote="REMOTE"
        branch="BRANCH" />
    <repository name="REPO"
        dir="DIR"
        remote="REMOTE"
        branch="BRANCH" />
    <product name="PROD"/>
</origin>
"""
        def parsedXml = xp.parseText(xml)
        def result = (Origin)this.parser.parse(parsedXml)
        assert result.name == "ORIGIN"
        assert result.products.size() == 1
        assert result.watchers.size() == 0
        assert result.repositories.size() == 2
    }


    void testParseProjectWithUnknownChildNodeShouldThrowConfigError() {
        def xml = """\
<project name="PROJ">
    <fake-node value="foo" />
</project>
"""
        def parsedXml = xp.parseText(xml)
        shouldFail ConfigError, {
            def result = this.parser.parse(parsedXml)
        }
    }

    void testSmallValidConfigurationWithAllFeatureTagsShouldReturnArrayOfProjects(){
        def xml = """\
<?xml version="1.0"?>
<!DOCTYPE projects SYSTEM "config/config.dtd">
<projects>
    <project-info name="projname">
        <coverity />
        <doc />
        <trigger polling="POLL" />
        <pm name="PM" email="pm@mail"/>
        <techlead name="tech lead" email="tl@mail"/>
        <watcher name ="watcher" email="watcher@mail" />
    </project-info>
    <project name="projname">
        <origin name="oriname">
            <repository name="reponame"
                dir="repodir"
                remote="reporemote"
                branch="repobranch"/>
            <product name="prodname"/>
        </origin>
    </project>
</projects>
"""
        def parsedXml = ValidatingXmlParserFactory.getXmlParser().parseText(xml)
        Project[] projects = (Project[]) this.parser.parse(parsedXml)

        assert projects.size() == 2
        Project projInfo = projects[0]
        assert projInfo.name == "projname"
        assert projInfo.pm.name == "PM"
        assert projInfo.techLead.email == "tl@mail"
        assert projInfo.trigger.enabled == true
        assert projInfo.trigger.polling == "POLL"
        assert projInfo.doc.enabled == true
        assert projInfo.origins.size() == 0
        Project proj = projects[1]
        assert proj.name == "projname"
        assert proj.origins.size() == 1
    }


    void testParsingMultiProjectRepoProductConfigurationShouldReturnArrayOfProjects()
    {
        def xml = """\
<?xml version="1.0"?>
<!DOCTYPE projects SYSTEM "config/config.dtd">
<projects>
    <project-info name="projname1">
        <pm name="PM1" email="pm1@mail"/>
        <techlead name="tech lead" email="tl@mail"/>
    </project-info>
    <project-info name="projname_b">
        <pm name="PM_B" email="pmb@mail"/>
        <techlead name="tech lead" email="tl@mail"/>
    </project-info>
    <project name="projname1">
        <origin name="oriname11">
            <repository name="reponame111"
                dir="repodir111"
                remote="reporemote111"
                branch="repobranch111"/>
            <product name="prodname111"/>
        </origin>
    </project>
    <project name="projname_b">
        <origin name="orinameB1">
            <repository name="reponameB11"
                dir="repodirB11"
                remote="reporemoteB11"
                branch="repobranchB11"/>
            <product name="prodnameB11"/>
        </origin>
        <origin name="orinameB2">
            <repository name="reponameB21"
                   dir="repodirB21"
                   remote="reporemoteB21"
                   branch="repobranchB21"/>
            <repository name="reponameB22"
                   dir="repodirB22"
                   remote="reporemoteB22"
                   branch="repobranchB22"/>
            <product name="prodnameB21"/>
            <product name="prodnameB22"/>
        </origin>
    </project>
</projects>
"""
        def parsedXml = ValidatingXmlParserFactory.getXmlParser().parseText(xml)
        Project[] projects = (Project[]) this.parser.parse(parsedXml)

        assert projects.size() == 4
        Project projB = projects[1]
        assert projB.name == "projname_b"
        assert projB.origins.size() == 0

        Origin origin2 = projects[3].origins[1]
        assert origin2.products.size() == 2
        assert origin2.repositories.size() == 2
    }
}
