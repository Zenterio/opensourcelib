package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.configuration.BuildTimeoutPolicy
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobBuildTimeoutModel
import javaposse.jobdsl.dsl.Job

class JobBuildTimeoutGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobBuildTimeoutModel m = (JobBuildTimeoutModel) model
        Job job = (Job) entity

        job.with {
            wrappers {
                timeout {
                    switch (m.policy) {
                        case BuildTimeoutPolicy.ABSOLUTE:
                            absolute(m.minutes)
                            break
                        case BuildTimeoutPolicy.ELASTIC:
                            elastic(m.elasticTimeOvershoot, m.elasticMinBuilds, m.minutes)
                            break
                    }

                    if (m.failBuild) {
                        failBuild()
                    } else {
                        abortBuild()
                    }

                    writeDescription(m.description)
                }
            }
            if(m.configurable) {
                configure { Node node ->
                    def target = getVariableXMLElement(node, getVariableXMLElementName(m.policy))
                    target.setValue("\${${JobBuildTimeoutModel.TIME_OUT_VARIABLE}}")
                }
            }
        }
    }

    private static String getVariableXMLElementName(BuildTimeoutPolicy policy) {
        switch (policy) {
            case BuildTimeoutPolicy.ABSOLUTE:
                return 'timeoutMinutes'
            case BuildTimeoutPolicy.ELASTIC:
                return 'timeoutMinutesElasticDefault'
            default:
                return ''

        }
    }

    private static Node getVariableXMLElement(Node node, String elementName) {
        return node / 'buildWrappers' / 'hudson.plugins.build__timeout.BuildTimeoutWrapper' / 'strategy' / elementName
    }
}
