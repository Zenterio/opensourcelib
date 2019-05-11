package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.DownStreamTriggerParameter
import com.zenterio.jenkins.models.job.JobDownStreamTriggerModel

class JobDownStreamTriggerBuildStepGenerator implements IPropertyGenerator{

    public void generate(ModelProperty model, Object entity) {
        JobDownStreamTriggerModel m = (JobDownStreamTriggerModel) model
        entity.with {
            publishers {
                downstreamParameterized {
                    m.parameters.each { DownStreamTriggerParameter param ->
                        trigger(param.jobName) {
                            if (m.block) {
                                block {
                                    buildStepFailure("FAILURE")
                                    failure("FAILURE")
                                    unstable("UNSTABLE")

                                }
                            }
                            parameters {
                                if (param.currentBuild) {
                                    currentBuild()
                                    nodeLabel("node", param.nodeLabel)
                                    predefinedProp("kfs_build_number", "\${BUILD_NUMBER}")
                                } else {
                                    propertiesFile(param.propertiesFile)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
