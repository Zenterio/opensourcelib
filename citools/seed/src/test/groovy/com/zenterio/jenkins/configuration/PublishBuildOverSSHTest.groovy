package com.zenterio.jenkins.configuration

class PublishBuildOverSSHTest extends GroovyTestCase {

    public void testDeepClone() {
        PublishBuildOverSSH data = PublishBuildOverSSH.testData
        PublishBuildOverSSH clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }

    public void testDefaultValues() {
        PublishBuildOverSSH publish =
            new PublishBuildOverSSH(null, 'name', 'server', "image", null,
                                        "rootDir", null, null,
                                         null, null, null)
        assert publish.enabled
        assert publish.name == 'name'
        assert publish.server == 'server'
        assert publish.artifactPattern == 'image'
        assert publish.removePrefix == ''
        assert publish.rootDir == 'rootDir'
        assert publish.numberOfBuildsToKeep == 5
        assert publish.productAltName == '${product_alt_name}'
        assert publish.retryTimes == 0
    }

}
