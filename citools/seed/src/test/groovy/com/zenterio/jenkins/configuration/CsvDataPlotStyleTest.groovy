package com.zenterio.jenkins.configuration

class CsvDataPlotStyleTest extends GroovyTestCase {

    public void testStringConversion() {
        CsvDataPlotStyle.values().each({ CsvDataPlotStyle style ->
            assert CsvDataPlotStyle.getFromString("${style}") == style
        })
    }
}
