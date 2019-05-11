package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.AutoCloneStyle
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone(style=AutoCloneStyle.COPY_CONSTRUCTOR)
class CsvDataPlot extends BaseConfig {

    /**
     * Input (source) CSV file
     */
    final String input

    /**
     * Plot title
     */
    final String title

    /**
     * Plot group
     */
    final String group

    /**
     * Scale, plot y-axis label
     */
    final String scale

    /**
     * Minimum y-axis value
     */
    final Double yMin

    /**
     * Maximum y-axis value
     */
    final Double yMax

    /**
     * Plot style
     */
    final CsvDataPlotStyle style

    /**
     * True if CSV data plot feature turned on.
     */
    final Boolean enabled

    CsvDataPlot(String input, String title, String group,
            String scale, Double yMin, Double yMax,
            CsvDataPlotStyle style, Boolean enabled) {
        this.enabled = enabled ?: false
        this.input = input ?: ""
        this.title = title ?: ""
        this.group = group ?: ""
        this.scale = scale ?: ""
        this.yMin = yMin
        this.yMax = yMax
        this.style = style
    }

    public static CsvDataPlot getTestData() {
        CsvDataPlot data = new CsvDataPlot("data.csv", "Title", "Group", "Scale",
            0, 1, CsvDataPlotStyle.AREA, true)
        return data
    }

}
