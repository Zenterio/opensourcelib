package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.configuration.CredentialList

class JobCredentialListModel extends ModelProperty {

    CredentialList credentials

    public JobCredentialListModel(CredentialList credentials) {
        super()
        this.credentials = credentials
    }
}
