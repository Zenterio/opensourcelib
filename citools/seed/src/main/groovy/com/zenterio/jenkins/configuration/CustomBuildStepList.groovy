package com.zenterio.jenkins.configuration

import java.util.List;

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class CustomBuildStepList extends ArrayList<CustomBuildStep> {

    @Override
    public CustomBuildStepList clone() {
        return this.collect{ CustomBuildStep buildStep ->
            buildStep.clone()
        } as CustomBuildStepList
    }

    /**
     * Returns list with enabled build-steps matching the supplied mode.
     * @param customBuildSteps
     * @param mode
     * @return
     */
    public CustomBuildStepList getFilteredCustomBuildSteps(CustomBuildStepMode mode) {
        return this.findAll { CustomBuildStep buildStep ->
            (buildStep.mode == mode) && (buildStep.enabled)
        } as CustomBuildStepList
    }

    public CustomBuildStepList getEnabled() {
        return this.findAll{ CustomBuildStep buildStep ->
            buildStep.enabled == true
        } as CustomBuildStepList
    }

    public static CustomBuildStepList getTestData() {
        return [CustomBuildStep.testData,
                CustomBuildStep.testData] as CustomBuildStepList
    }
}
