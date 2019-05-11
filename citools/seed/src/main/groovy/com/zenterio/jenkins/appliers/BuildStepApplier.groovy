package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.configuration.CustomBuildStep
import com.zenterio.jenkins.configuration.CustomBuildStepList
import com.zenterio.jenkins.configuration.CustomBuildStepMode
import com.zenterio.jenkins.configuration.CustomBuildStepType
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobShellStepModel
import com.zenterio.jenkins.models.job.JobSystemGroovyScriptStepModel
import groovy.util.logging.Log

@Log
class BuildStepApplier {

    protected BuildStepFactory buildStepFactory

    public BuildStepApplier(BuildStepFactory buildStepFactory) {
        this.buildStepFactory = buildStepFactory
    }

    public void applyBuildSteps(List<String> defaultBuildSteps,
                                CustomBuildStepList customBuildSteps,
                                int swUpgradeOffset, IModel job) {
        CustomBuildStepList customBuildStepsPrepend =
            customBuildSteps.getFilteredCustomBuildSteps(CustomBuildStepMode.PREPEND)
        CustomBuildStepList customBuildStepsOverride =
            customBuildSteps.getFilteredCustomBuildSteps(CustomBuildStepMode.OVERRIDE)
        CustomBuildStepList customBuildStepsOverrideNamed =
                customBuildSteps.getFilteredCustomBuildSteps(CustomBuildStepMode.OVERRIDE_NAMED)
        CustomBuildStepList customBuildStepsAppend =
            customBuildSteps.getFilteredCustomBuildSteps(CustomBuildStepMode.APPEND)
        this.applyCustomBuildSteps(job, customBuildStepsPrepend, swUpgradeOffset)
        if (customBuildStepsOverride.size() > 0) {
            this.applyCustomBuildSteps(job, customBuildStepsOverride, swUpgradeOffset)
        } else {
            this.applyNamedBuildSteps(job, defaultBuildSteps, customBuildStepsOverrideNamed, swUpgradeOffset)
        }
        this.applyCustomBuildSteps(job, customBuildStepsAppend, swUpgradeOffset)
    }

    /**
     * Adds a list of custom build steps. No check if the steps are enabled.
     * Will apply them anyway.
     * @param job   The job which to add the build steps to.
     * @param steps Custom build steps to add
     * @param swUpgradeOffset SW upgrade offset
     */
    public void applyCustomBuildSteps(IModel job, CustomBuildStepList steps,
            int swUpgradeOffset) {
        steps.each({ CustomBuildStep step ->
            log.finer("Adding custom build step")
            def scriptlet = this.buildStepFactory.fromString(step.code, swUpgradeOffset)
            switch (step.type) {
                case CustomBuildStepType.SHELL:
                    job << new JobShellStepModel(scriptlet)
                    break
                case CustomBuildStepType.SYSTEM_GROOVY:
                    job << new JobSystemGroovyScriptStepModel(scriptlet)
                    break
                default:
                    throw new IllegalArgumentException("Could not create a model for a custom buildstep of type ${step.type}!")
            }
        })
    }

    /**
     * Adds a list of named build steps
     * @param job   The job which to add the build steps to.
     * @param steps Named build steps to add
     * @param swUpgradeOffset SW upgrade offset
     */
    public void applyNamedBuildSteps(IModel job, List<String> steps, CustomBuildStepList overrideNamedSteps, int swUpgradeOffset) {
        steps.each({ String buildStepName ->

            def step = findOverrideForName(buildStepName, overrideNamedSteps)

            if (step == null) {
                log.finer("Adding named build step (name=${buildStepName})")
                def scriptlet = this.buildStepFactory.fromName(buildStepName, swUpgradeOffset)
                job << new JobShellStepModel(scriptlet)
            } else {
                log.finer("Overriding named build step (name=${buildStepName})")
                def scriptlet = this.buildStepFactory.fromString(step.code, swUpgradeOffset)
                job << new JobShellStepModel(scriptlet)
            }


        })
    }

    private CustomBuildStep findOverrideForName(name, CustomBuildStepList customBuildStepsOverrideNamed) {
        return customBuildStepsOverrideNamed.find {step -> step.overrideName == name}
    }
}
