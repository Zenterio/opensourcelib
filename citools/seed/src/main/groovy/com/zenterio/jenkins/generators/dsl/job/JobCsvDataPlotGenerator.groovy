package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobCsvDataPlotModel
import com.zenterio.jenkins.configuration.CsvDataPlot


class JobCsvDataPlotGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobCsvDataPlotModel m = (JobCsvDataPlotModel) model;
        if (m.configs.length > 0) {
            entity.with {
                publishers {
                    plotBuildData {
                        m.configs.each({ CsvDataPlot config ->
                            plot(config.group, "data_${ (new File(config.input)).getName() }") {
                                title(config.title)
                                yAxis(config.scale)
                                yAxisMinimum(config.yMin)
                                yAxisMaximum(config.yMax)
                                style("${config.style}")
                                excludeZero()
                                keepRecords()
                                csvFile(config.input) {
                                }
                            }
                        })
                    }
                }
            }
        }
    }

}
