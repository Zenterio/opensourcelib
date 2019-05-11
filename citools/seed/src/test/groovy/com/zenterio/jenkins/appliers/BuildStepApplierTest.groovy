package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.configuration.CustomBuildStep
import com.zenterio.jenkins.configuration.CustomBuildStepList
import com.zenterio.jenkins.configuration.CustomBuildStepMode
import com.zenterio.jenkins.configuration.CustomBuildStepType
import com.zenterio.jenkins.configuration.VariableCollection
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.models.IModel
import groovy.mock.interceptor.StubFor

public class BuildStepApplierTest extends GroovyTestCase {

    void testApplyBuildStepsWithoutOverrides() {
        def custom = [new CustomBuildStep("pre", CustomBuildStepMode.PREPEND, true),
                      new CustomBuildStep("append", CustomBuildStepMode.APPEND, true)] as CustomBuildStepList
        def named = ["named"]
        IModel job = new ModelEntity()
        def stub = new StubFor(BuildStepFactory)
        stub.demand.with {
            fromName { String name, int offset -> return name }
            fromString { String code, int offset-> return code }
            fromString { String code, int offset-> return code }
        }
        stub.use({
            def factory = new BuildStepFactory("", new VariableCollection(), {})
            def applier = new BuildStepApplier(factory)
            applier.applyBuildSteps(named, custom, 0, job)

            def children = job.getChildren()
            assert children.size() == 3
            assert children[0].script == "pre"
            assert children[1].script == "named"
            assert children[2].script == "append"
        })
    }

    void testApplyBuildStepsWithOverrides() {
        def custom = [new CustomBuildStep("pre", CustomBuildStepMode.PREPEND, true),
                      new CustomBuildStep("override", CustomBuildStepMode.OVERRIDE, true),
                      new CustomBuildStep("append", CustomBuildStepMode.APPEND, true)] as CustomBuildStepList
        def named = ["named"]
        IModel job = new ModelEntity()
        def stub = new StubFor(BuildStepFactory)
        stub.demand.with {
            fromString { String code, int offset-> return code }
            fromString { String code, int offset-> return code }
            fromString { String code, int offset-> return code }
        }
        stub.use({
            def factory = new BuildStepFactory("", new VariableCollection(), {})
            def applier = new BuildStepApplier(factory)
            applier.applyBuildSteps(named, custom, 0, job)

            def children = job.getChildren()
            assert children.size() == 3
            assert children[0].script == "pre"
            assert children[1].script == "override"
            assert children[2].script == "append"
        })
    }

    void testApplyBuildStepsWithOverrideNameds() {
        def custom = [new CustomBuildStep("pre", CustomBuildStepMode.PREPEND, true),
                      new CustomBuildStep("override2", CustomBuildStepMode.OVERRIDE_NAMED, true, CustomBuildStep.DEFAULT_TYPE, 'named2'),
                      new CustomBuildStep("append", CustomBuildStepMode.APPEND, true)] as CustomBuildStepList
        def named = ["named1", "named2", "named3"]
        IModel job = new ModelEntity()
        def stub = new StubFor(BuildStepFactory)
        stub.demand.with {
            fromName { String code, int offset-> return code }
            fromName { String code, int offset-> return code }
            fromString { String code, int offset-> return code }
            fromString { String code, int offset-> return code }
            fromString { String code, int offset-> return code }
        }
        stub.use({
            def factory = new BuildStepFactory("", new VariableCollection(), {})
            def applier = new BuildStepApplier(factory)
            applier.applyBuildSteps(named, custom, 0, job)

            def children = job.getChildren()
            assert children.size() == 5
            assert children[0].script == "pre"
            assert children[1].script == "named1"
            assert children[2].script == "override2"
            assert children[3].script == "named3"
            assert children[4].script == "append"
        })
    }
}
