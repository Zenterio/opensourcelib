package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.ProductVariant

class ConfigXmlParserProductVariantTest extends ConfigXmlParserTestCase
{

    private List<String> variants = ['debug', 'release', 'production']

    void testParseEmptyProductVariant() {
        this.variants.each { String variant ->
            super.setUp(variant)
            ProductVariant result = this.parse("""<${variant}/>""")
            assert result.description == null
            assert result.enabled == true
        }
    }

    void testParseDisabledProductVariant() {
        this.variants.each { String variant ->
            super.setUp(variant)
            String xml = """<${variant} enabled="false" />"""
            ProductVariant result = this.parse(xml)
            assert result.enabled == false
        }
    }

    void testParseFullProductVariant() {
        this.variants.each { String variant ->
            super.setUp(variant)
            String xml = """\
<${variant}>
    <cache ccache-enabled="false" />
    <csv-data-plot />
    <csv-data-plot />
    <publish-build-over-ssh
        enabled="false" name="N"
        server="S"
        artifact-pattern=""
        root-dir="" />
    <publish-over-ssh server="S" enabled="false">
        <transfer-set src="src" />
    </publish-over-ssh>
    <sw-upgrade offset="7"/>
    <sw-upgrade offset="3"/>
    <test-group name="tg"
            test-root="root"
            stb-label="stb"
            box-configuration="config"
            product-configuration="product" >
        <repository name="repo1" dir="dir" remote="remote" branch="b" />
        <test-context name="tc">
            <test-suite path="path" />
        </test-context>
    </test-group>
    <build-env enabled="false" />
    <build-timeout policy="absolute" minutes="5" />
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
    <resources name="N" />
    <variable name="var-name">var-value</variable>
    <watcher name ="watcher" email="watcher@example.com" />
    <watcher name ="second watcher" email="second.watcher@example.com" />
    <workspace-browsing enabled="false" />
</${variant}>
"""
            ProductVariant result = this.parse(xml)
            assert result.buildType.name == variant
            assert result.enabled == true
            assert result.csvDataPlots.length == 2
            assert result.swUpgrades.size() == 2
            assert result.swUpgrades[0].offset == 7
            assert result.swUpgrades[1].offset == 3
            assert result.testGroups.size() == 1
            assert result.buildEnv.enabled == false
            assert result.buildTimeout.minutes == 5
            assert result.cache.ccacheEnabled == false
            assert result.credentials.size() == 2
            assert result.customBuildSteps.size() == 2
            assert result.description.description == "DESC"
            assert result.incremental.enabled == true
            assert result.logParsing.enabled == true
            assert result.makePrefix.value == "makeprefix"
            assert result.makeRoot.name == "makeroot"
            assert result.makeTarget.name == "maketarget"
            assert result.resources.name == "N"
            assert result.variables.size() == 1
            assert result.watchers.size() == 2
            assert result.workspaceBrowsing.enabled == false
        }
    }
}
