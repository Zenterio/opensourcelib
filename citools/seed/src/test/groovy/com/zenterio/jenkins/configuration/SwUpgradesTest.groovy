package com.zenterio.jenkins.configuration

class SwUpgradesTest extends GroovyTestCase {

    public void testDeepClone() {
        SwUpgrades swUpgrades = SwUpgrades.testData
        SwUpgrades clone = swUpgrades.clone()
        assert swUpgrades == clone
        swUpgrades.eachWithIndex { SwUpgrade original, int i ->
            assert !original.is(clone[i])
        }
    }

    public void testGetEnabledWithSomeEnabled() {
        SwUpgrades swUpgrades = SwUpgrades.testData
        SwUpgrade swUpgrade = new SwUpgrade(0, false)
        swUpgrades.add(swUpgrade)
        assert swUpgrades.getEnabled() == SwUpgrades.testData
        assert swUpgrades != SwUpgrades.testData
    }

    public void testGetEnabledWithOnlyDisabled() {
        SwUpgrade swUpgrade = new SwUpgrade(0, false)
        SwUpgrades swUpgrades = [ swUpgrade ] as SwUpgrades
        assert swUpgrades.getEnabled().size() == 0
    }
}
