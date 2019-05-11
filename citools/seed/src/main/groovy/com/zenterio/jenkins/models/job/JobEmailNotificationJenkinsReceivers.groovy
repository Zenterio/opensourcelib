package com.zenterio.jenkins.models.job

import groovy.transform.TupleConstructor

@TupleConstructor
class JobEmailNotificationJenkinsReceivers {
    final Boolean requester
    final Boolean developers
    final Boolean culprits
}
