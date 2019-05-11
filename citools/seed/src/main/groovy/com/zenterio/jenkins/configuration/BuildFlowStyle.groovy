package com.zenterio.jenkins.configuration

enum BuildFlowStyle {
    ZIDS_UNIT_TEST_PARALLEL('zids-unit-test-parallel'),
    ZIDS_UNIT_TEST_SERIAL('zids-unit-test-serial')

    String name

    BuildFlowStyle(String name) {
        this.name = name
    }

    @Override
    String toString() {
        return this.name
    }
}