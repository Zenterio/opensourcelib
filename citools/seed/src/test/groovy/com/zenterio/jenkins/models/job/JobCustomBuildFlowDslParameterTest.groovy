package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.job.flowdsl.BuildFlowDslParameter
import com.zenterio.jenkins.models.job.flowdsl.FlowJobFlowDslStepModel
import com.zenterio.jenkins.models.job.flowdsl.JobBuildFlowDslExcludeFromFlowModel
import com.zenterio.jenkins.models.job.flowdsl.JobBuildFlowDslParameterBuildNumberModel


class JobCustomBuildFlowDslParameterTest extends GroovyTestCase {

    public void testCustomParameterBuildNumber() {
        FlowJobFlowDslStepModel dsl = new FlowJobFlowDslStepModel([new BuildFlowDslParameter("global", "\"value\"")] as BuildFlowDslParameter[])

        BaseJobModel root = new FlowJobModel().with {
            add new JobNameModel("root")
            add dsl
            add new JobModel().with {
                BaseJobModel c1 = it
                add new JobNameModel("C-1")
                add new JobModel().with {
                    add new JobNameModel("C11")
                    add new JobBuildFlowDslParameterBuildNumberModel("BUILD_NUMBER")
                    add new JobModel().with {
                        add new JobNameModel("C21")
                        add new JobBuildFlowDslParameterBuildNumberModel("build", c1)
                    }
                }

            }
            add new JobModel().with {
                add new JobNameModel("C2")
                add new JobBuildFlowDslParameterBuildNumberModel("build-number")
            }
        }

        String expected = """\
def build_root = build;
parallel(
  {
    build_C_1 = build("C-1", global: "value");
    build_C11 = build("C11", global: "value", BUILD_NUMBER: build_C_1.build.number);
    build_C21 = build("C21", global: "value", build: build_C_1.build.number);
  },{
    build_C2 = build("C2", global: "value", build-number: build_root.build.number);
  }
);
"""
        assert expected == dsl.getScript()
    }

    public void testCustomParamterBuildNumberThrowsExceptionIfNoParent() {
        FlowJobFlowDslStepModel dsl = new FlowJobFlowDslStepModel([new BuildFlowDslParameter("global", "\"value\"")] as BuildFlowDslParameter[])
        BaseJobModel root = new FlowJobModel().with {
            add new JobNameModel("root")
            add dsl
            add new JobBuildFlowDslParameterBuildNumberModel("build-number")
        }
        shouldFail(RuntimeException, {
            dsl.getScript()
        })
    }

    public void testExcludeFromFlow() {
        FlowJobFlowDslStepModel dsl = new FlowJobFlowDslStepModel()
        BaseJobModel root = new FlowJobModel().with {
            add new JobNameModel("root")
            add dsl
            add new BaseJobModel().with {
                add new JobNameModel("C1")
                add new BaseJobModel().with {
                    add new JobNameModel("C11")
                    add new JobBuildFlowDslExcludeFromFlowModel()
                    add new BaseJobModel().with {
                        add new JobNameModel("C111")
                    }
                }
            }
        }
        String expected = """\
def build_root = build;
build_C1 = build("C1");
"""
                assert expected == dsl.getScript()
    }

}

