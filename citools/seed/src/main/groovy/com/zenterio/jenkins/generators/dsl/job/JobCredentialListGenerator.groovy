package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.configuration.Credential
import com.zenterio.jenkins.configuration.CredentialType
import com.zenterio.jenkins.configuration.CredentialList
import com.zenterio.jenkins.generators.IPropertyGenerator;
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobCredentialListModel


class JobCredentialListGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        JobCredentialListModel m = (JobCredentialListModel) model
        CredentialList enabledCredentials = m.credentials.getEnabled()

        if (!enabledCredentials.empty) {
            entity.with {
                wrappers {
                    credentialsBinding {
                        enabledCredentials.each { Credential credential ->
                            switch(credential.type) {
                                case CredentialType.FILE:
                                    file(credential.variableName, credential.id)
                                    break
                                case CredentialType.TEXT:
                                    string(credential.variableName, credential.id)
                                    break
                                case CredentialType.USERNAME_PASSWORD:
                                    usernamePassword(credential.variableName + "_USERNAME",
                                                     credential.variableName + "_PASSWORD",
                                                     credential.id)
                                    break
                            }
                        }
                    }
                }
            }
        }
    }
}
