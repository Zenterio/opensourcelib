package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Cache extends BaseConfig {

    static String ARTIFACTORY_CREDENTIAL_ID = "jenkins-artifactory-user"

    /**
     * True if ccache feature turned on
     */
    Boolean ccacheEnabled

    /**
     * True if mcache feature turned on
     */
    Boolean mcacheEnabled

    /**
     * True if ccache should be published after the job is complete
     */
    Boolean ccachePublish

    /**
     * True if mcache should be published after the job is complete
     */
    Boolean mcachePublish

    /**
     * The maximum size of the CCache
     */
    CcacheSize ccacheSize

    /**
     * Relative storage path where to store the CCache
     */
    String ccacheStorage

    /**
     *
     * @param ccacheEnabled    If ccache should be enabled or not.
     * @param ccachePublish    If the ccache should be published
     * @param ccacheSize    The size of the cache
     * @param ccacheStorage    The storage place for the cache
     * @param mcacheEnabled    If distributed mcache should be enabled or not
     * @param mcachePublish    If mcache should be published
     */
    public Cache(Boolean ccacheEnabled, Boolean ccachePublish, CcacheSize ccacheSize, String ccacheStorage, Boolean mcacheEnabled, Boolean mcachePublish) {
        this.ccacheEnabled = ccacheEnabled
        this.mcacheEnabled = mcacheEnabled
        this.ccachePublish = ccachePublish
        this.mcachePublish = mcachePublish
        this.ccacheSize = ccacheSize
        this.ccacheStorage = ccacheStorage ?: ""
    }

    public CcacheSize getCcacheSize() {
        if (this.ccachePublish) {
            return this.ccacheSize
        } else {
            return CcacheSize.OVER_SIZE
        }
    }

    public Cache createDisabled() {
        Cache result = this.clone()
        result.ccacheEnabled = false
        result.mcacheEnabled = false
        return result
    }

    public static Cache getTestData() {
        return new Cache(true, true, CcacheSize.MEDIUM, "storage", true, true)
    }
}
