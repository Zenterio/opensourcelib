package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.ConfigAction;
import com.zenterio.jenkins.configuration.XmlData;
import com.zenterio.jenkins.configuration.XmlDataOperation;
import com.zenterio.jenkins.configuration.XmlToCsv;


class ConfigXmlParserXmlToCsvTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseXmlToCsvWithOneData() {
        def xml = """
<xml-to-csv input="data.xml" output="data.csv">
    <xml-data source="source.in.xml" operation="min" field="Field" caption="Caption"/>
</xml-to-csv>
"""
        def parsedXml = xp.parseText(xml)
        XmlToCsv result = this.parser.parse(parsedXml)
        assert result.input == "data.xml"
        assert result.output == "data.csv"
        assert result.data.length == 1
        XmlData data = result.data[0]
        assert data.source == "source.in.xml"
        assert data.operation == XmlDataOperation.MIN
        assert data.field == "Field"
        assert data.caption == "Caption"
    }

    void testParseXmlToCsvWithMultipleData() {
        def xml = """
<xml-to-csv input="data.xml" output="data.csv">
    <xml-data source="source.in.xml" operation="min" field="Field" caption="Caption"/>
    <xml-data source="source.in.xml" operation="min" field="Field" caption="Caption"/>
    <xml-data source="source.in.xml" operation="min" field="Field" caption="Caption"/>
</xml-to-csv>
"""
        def parsedXml = xp.parseText(xml)
        XmlToCsv result = this.parser.parse(parsedXml)
        assert result.data.length == 3
    }


    void testParseXmlDataOperations() {
        ['avg', 'min', 'max'].each { String op ->
            def xml ="""<xml-data source="" operation="${op}" field="" caption=""/>"""
            def parsedXml = xp.parseText(xml)
            XmlData result =  this.parser.parse(parsedXml)
            assert result.operation == XmlDataOperation.getFromString(op)
        }
    }

}
