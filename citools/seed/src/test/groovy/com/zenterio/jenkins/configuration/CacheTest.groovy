package com.zenterio.jenkins.configuration

class CacheTest extends GroovyTestCase {

    public void testDeepCloneEquals() {
        Cache cache = Cache.testData
        Cache clone = cache.clone()

        assert cache == clone
        assert !cache.is(clone)
    }

    public void testOverSizeWhenPublishIsDisabled() {
        Cache cache = new Cache(true, false, CcacheSize.SMALL, "storage", false, true)
        assert cache.ccacheSize == CcacheSize.OVER_SIZE
    }

    public void testCreateDisabledReturnsNewInstanceButDisabled() {
        Cache enabled = Cache.testData
        Cache disabled = enabled.createDisabled()
        assert enabled.ccacheEnabled == true
        assert enabled.mcacheEnabled == true
        assert enabled.ccachePublish == disabled.ccachePublish
        assert enabled.mcachePublish == disabled.mcachePublish
        assert enabled.ccacheSize == disabled.ccacheSize
        assert enabled.ccacheStorage == disabled.ccacheStorage
    }
}
