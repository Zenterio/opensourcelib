package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.TransferSet

class ConfigXmlParserTransferSetTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    @Override
    protected void setUp() throws Exception {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    public void testParseWithAllAttributeValid() {
        def xml = """<transfer-set src="SRC" remove-prefix="PREFIX" remote-dir="DIR" exclude-files="EXCLUDE_FILES"
                                   pattern-separator="||" no-default-excludes="true" make-empty-dirs="true" flatten-files="true"
                                   remote-dir-is-date-format="true" exec-timeout-ms="666" exec-in-pseudo-tty="true">COMMAND</transfer-set>"""
        def parsedXml = xp.parseText(xml)
        TransferSet transfer = this.parser.parseTransferSet(parsedXml) as TransferSet

        assert transfer.src == 'SRC'
        assert transfer.remoteDir == 'DIR'
        assert transfer.removePrefix == 'PREFIX'
        assert transfer.excludeFiles == 'EXCLUDE_FILES'
        assert transfer.patternSeparator == '||'
        assert transfer.noDefaultExcludes
        assert transfer.makeEmptyDirs
        assert transfer.flattenFiles
        assert transfer.remoteDirIsDateFormat
        assert transfer.execTimeout == 666
        assert transfer.execInPTTY
        assert transfer.command == 'COMMAND'
    }

    public void testParseWithDefaultAttributeValues() {
        def xml = """<transfer-set>COMMAND</transfer-set>"""
        def parsedXml = xp.parseText(xml)
        TransferSet transfer = this.parser.parseTransferSet(parsedXml) as TransferSet

        assert transfer.src == ''
        assert transfer.remoteDir == ''
        assert transfer.removePrefix == ''
        assert transfer.excludeFiles == ''
        assert transfer.patternSeparator == '[, ]+'
        assert !transfer.noDefaultExcludes
        assert !transfer.makeEmptyDirs
        assert !transfer.flattenFiles
        assert !transfer.remoteDirIsDateFormat
        assert transfer.execTimeout == 120000
        assert !transfer.execInPTTY
        assert transfer.command == 'COMMAND'
    }
}
