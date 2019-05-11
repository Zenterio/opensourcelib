package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.CsvDataPlot


class ConfigXmlParserCsvDataPlotTest extends GroovyTestCase {
    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false, true)
        this.parser = new ConfigXmlParser()
    }

    private Object parse(String xml) {
        return this.parser.parse(this.xp.parseText(xml))
    }

    void testParseCsvDataPlotDefaultEnabled() {
        CsvDataPlot result = this.parse("""<csv-data-plot input="result/data.csv" title="Title" group="Group" scale="Y-axis label" y-min="0" y-max="1" style="bar"/>""")
        assert result.input == "result/data.csv"
        assert result.title == "Title"
        assert result.group == "Group"
        assert result.scale == "Y-axis label"
        assert result.yMin == 0
        assert result.yMax == 1
        assert result.enabled == true
    }

    void testParseCsvDataPlotDisabled() {
        CsvDataPlot result = this.parse("""<csv-data-plot enabled="false" />""")
        assert result.enabled == false
    }
}
