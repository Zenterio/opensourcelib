package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Trigger extends BaseConfig {

    String polling
    String periodic
    Boolean acceptNotifyCommit
    Boolean enabled

    /**
     *
     * @param polling               Cron string for SCM polling frequency.
     * @param periodic              Cron string job trigger frequency.
     * @param acceptNotifyCommit    Accept notifyCommit
     * @param enabled               Enable trigger at all.
     */
    public Trigger(String polling, String periodic, Boolean acceptNotifyCommit, Boolean enabled) {
        this.polling = polling
        this.periodic = periodic
        this.acceptNotifyCommit = acceptNotifyCommit
        this.enabled = enabled
        /* SCM polling can not be empty in order for notifyCommit to work on Jenkins */
        if (this.acceptNotifyCommit && this.polling == null) {
            this.polling = ' '
        }
    }

    public Boolean getValid() {
        return (this.periodic != null) || (this.polling != null) || (this.acceptNotifyCommit)
    }
}
