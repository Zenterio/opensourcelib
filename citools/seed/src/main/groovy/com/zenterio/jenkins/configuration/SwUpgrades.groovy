package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class SwUpgrades extends ArrayList<SwUpgrade> {

    public Object clone() {
        return this.collect{ SwUpgrade swUpgrade ->
            swUpgrade.clone()
        } as SwUpgrades
    }

    public SwUpgrades getEnabled() {
        return this.findAll{ SwUpgrade swUpgrade ->
            swUpgrade.enabled == true
        } as SwUpgrades
    }

    public static SwUpgrades getTestData() {
        return [new SwUpgrade(3, true), new SwUpgrade(4, true)] as SwUpgrades
    }
}
