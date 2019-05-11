package com.zenterio.jenkins.configuration

class CustomBuildStepListTest extends GroovyTestCase {

    public void testDeepClone() {
        def lst = CustomBuildStepList.testData
        def clone = lst.clone()
        assert lst == clone
        assert !lst.is(clone)
        lst.eachWithIndex { CustomBuildStep original, int i ->
            assert original == clone[i]
            assert !original.is(clone[i])
        }
    }

    void testGetFilteredCustomBuildSteps() {
        def buildSteps = [new CustomBuildStep("", CustomBuildStepMode.PREPEND, true),
                          new CustomBuildStep("", CustomBuildStepMode.OVERRIDE, true),
                          new CustomBuildStep("", CustomBuildStepMode.APPEND, true),
                          new CustomBuildStep("", CustomBuildStepMode.PREPEND, false),
                          new CustomBuildStep("", CustomBuildStepMode.OVERRIDE, false),
                          new CustomBuildStep("", CustomBuildStepMode.APPEND, false)] as CustomBuildStepList

        def modesToTest = [CustomBuildStepMode.PREPEND, CustomBuildStepMode.OVERRIDE,
            CustomBuildStepMode.APPEND]

        modesToTest.eachWithIndex { CustomBuildStepMode mode, int index ->
            def filteredSteps = buildSteps.getFilteredCustomBuildSteps(mode)
            assert filteredSteps.size() == 1
            assert filteredSteps[0] == buildSteps[index]
        }
    }

    public void testGetEnabledWithSomeEnabled() {
        CustomBuildStepList buildSteps = CustomBuildStepList.testData
        buildSteps.add(new CustomBuildStep("", CustomBuildStepMode.PREPEND, false))
        assert buildSteps.enabled == CustomBuildStepList.testData
        assert buildSteps != CustomBuildStepList.testData
    }

    public void testGetEnabledWithOnlyDisabled() {
        CustomBuildStepList buildSteps =
            [new CustomBuildStep("", CustomBuildStepMode.APPEND, false)] as CustomBuildStepList
        assert buildSteps.enabled.size() == 0
    }
}
