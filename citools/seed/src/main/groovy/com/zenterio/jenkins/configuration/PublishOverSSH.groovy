package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class PublishOverSSH extends BaseConfig implements IVariableContext {
    /**
     * True if feature turned on
     */
    Boolean enabled;

    /**
     * The name of the SSH server to connect to.
     */
    String server;

    /**
     * Number of retries to connect to the server.
     */
    int retryTimes;

    /**
     * Delay between each retry in milli seconds.
     */
    int retryDelay;

    /**
     * The label for this Server instance - for use with Parameterized publishing.
     */
    String label;

    /**
     * List of TransferSet.
     */
    List<TransferSet> transferSets;

    VariableCollection variables


    public PublishOverSSH(Boolean enabled,
                      String server,
                      Integer retryTimes,
                      Integer retryDelay,
                      String label,
                      List<TransferSet> transferSets) {
        super();
        // Use required arguments and create default values inside the class instead...

        this.enabled = (enabled == null) ? true : enabled
        this.server = server
        this.retryTimes = retryTimes ?: 0
        this.retryDelay = retryDelay ?: 10000
        this.label = label ?: ""
        this.transferSets = transferSets ?: new ArrayList<TransferSet>()
        this.variables = new VariableCollection()

        if (!this.server && this.enabled) {
            throw new IllegalArgumentException("Must provide a server if publish-over-ssh is enabled. (server=${this.server}, enabled=${enabled}")
        }
    }

    public PublishOverSSH(PublishOverSSH other) {
        this.enabled = other.enabled
        this.server = other.server
        this.retryTimes = other.retryTimes
        this.retryDelay = other.retryDelay
        this.label = other.label
        this.transferSets = other.transferSets.collect{ TransferSet transfer -> transfer.clone() } as ArrayList<TransferSet>
        this.variables = other.variables?.clone()
    }

    public PublishOverSSH clone() {
        return new PublishOverSSH(this)
    }

    public static PublishOverSSH getTestData() {
        return  new PublishOverSSH(null, 'server', null, null, null,
                [new TransferSet('SRC_1', 'DIR_1', null, null, null, null, null, null, null, null, null, null),
                 new TransferSet('SRC_1', 'DIR_1', null, null, null, null, null, null, null, null, null, null)])
    }
}
