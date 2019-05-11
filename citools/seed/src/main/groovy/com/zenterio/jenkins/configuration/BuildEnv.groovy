package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class BuildEnv extends BaseConfig {
    /**
     * True if build env should be used
     */
    Boolean enabled

    /**
     * The name of the environment to use
     */
    String env

    /**
     * The arguments to use when calling the build environment tool.
     * This overrides the env specific arguments
     */
    String args

    /**
     *
     * @param enabled    If build env should be enabled or not.
     * @param env        The name of the environment
     * @param args       Args to use. If null the default arguments for the image name will be used
     */
    public BuildEnv(Boolean enabled, String env, String args) {
        this.enabled = enabled
        this.env = env
        this.args = args
    }

    public static BuildEnv getTestData() {
        return new BuildEnv(true, "abs.u14", "--root")
    }

    public String getArgs() {
        if (this.args != null) {
            return this.args
        } else {
            if (this.env == null || this.env == '' || this.env.startsWith('abs.')) {
                return '''--mount type=bind,source=/dev/shm,target=/dev/shm --mount type=bind,source=/bin/true,target=/bin/chown --hostname "${HOSTNAME}_${EXECUTOR_NUMBER}"'''
            } else {
                return ''
            }
        }
    }

    private String getImageOption() {
        if (this.env != null && this.env != '') {
            return "--image ${this.env}"
        } else {
            return ""
        }
    }

    public String getPrefix() {
        String mounts = """--mount type=bind,source=/home/jenkins/.ssh/id_rsa,target=/root/.ssh/id_rsa,readonly --mount type=bind,source=/etc/ssh/ssh_known_hosts,target=/etc/ssh/ssh_known_hosts"""
        return """zebra ${getImageOption()} ${mounts} --network bridge --root --root-dir "\${WORKSPACE}" --container-root-dir /zebra/workspace -e WORKSPACE=/zebra/workspace ${this.getArgs()}"""
    }
}
