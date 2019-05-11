package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class PublishOverSSHList extends ArrayList<PublishOverSSH>{

    public PublishOverSSHList clone() {
        return this.collect{ PublishOverSSH publishOverSSH ->
            publishOverSSH.clone()
        } as PublishOverSSHList
    }

    public PublishOverSSHList getEnabled() {
        return this.findAll{ PublishOverSSH publishOverSSH -> publishOverSSH.enabled } as PublishOverSSHList
    }

    public static PublishOverSSHList getTestData() {
        PublishOverSSHList data = new PublishOverSSHList()
        data.add(new PublishOverSSH(true, 'Server', null, null, null, null))
        data.add(new PublishOverSSH(false, 'Server', null, null, null, null))
        data.add(new PublishOverSSH(true, 'Server', null, null, null, null))
        return data
    }
}
