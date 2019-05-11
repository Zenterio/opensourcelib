package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.configuration.CsvDataPlot

/**
 * Holds data related to simplified use of the plot+plugin with CSV file.
 */
class JobCsvDataPlotModel extends ModelProperty {

    CsvDataPlot[] configs

    JobCsvDataPlotModel(CsvDataPlot[] configs) {
        super()
        this.configs = configs
    }
}
