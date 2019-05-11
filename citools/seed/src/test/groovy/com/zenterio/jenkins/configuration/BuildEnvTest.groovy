package com.zenterio.jenkins.configuration

class BuildEnvTest extends GroovyTestCase {

    public void testDeepCloneEquals() {
        BuildEnv data = BuildEnv.testData
        BuildEnv clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }

    public void testArgsAreReturnedIfSet() {
        BuildEnv buildEnv = new BuildEnv(true, 'env', 'args')
        assert buildEnv.args == 'args'
    }

    public void testAbsDefaultArgsAreReturnedForAbsEnv() {
        BuildEnv buildEnv = new BuildEnv(true, 'abs.u14', null)
        assert buildEnv.args == '''--mount type=bind,source=/dev/shm,target=/dev/shm --mount type=bind,source=/bin/true,target=/bin/chown --hostname "${HOSTNAME}_${EXECUTOR_NUMBER}"'''
    }

    public void testAbsDefaultArgsAreReturnedForEmptyEnv() {
        BuildEnv buildEnv = new BuildEnv(true, '', null)
        assert buildEnv.args == '''--mount type=bind,source=/dev/shm,target=/dev/shm --mount type=bind,source=/bin/true,target=/bin/chown --hostname "${HOSTNAME}_${EXECUTOR_NUMBER}"'''
    }

    public void testEmptyStringIsReturnedForUnknownEnvAndNoArgs() {
        BuildEnv buildEnv = new BuildEnv(true, 'unknown', null)
        assert buildEnv.args == ''
    }

    public void testImageOptionNotInPrefixIfEnvNotSpecified() {
        BuildEnv buildEnv = new BuildEnv(true, '', null)
        assert ! buildEnv.prefix.contains('--image')
    }

    public void testImageOptionInPrefixIfEnvSpecified() {
        BuildEnv buildEnv = new BuildEnv(true, 'abs.u14', null)
        assert buildEnv.prefix.contains('--image')
    }
}
