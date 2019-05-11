package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Credential extends BaseConfig {

    /**
     * Describes what type of secret is to be shared.
     */
    CredentialType type

    /**
     * Uniquely identifies a credential stored in Jenkins global credentials domain.
     */
    String id

    /**
     * The name of the build variable to bind the secret to.
     *
     * @note  If the credential type is username/password and a variableName is
     *        provided, the resulting build variables will be postpended with
     *        _USERNAME and _PASSWORD.
     */
    String variableName

    /**
     * True if the credential feature is turned on and credentials should be bound.
     */
    Boolean enabled

    public Credential(CredentialType type, String id, String variableName, Boolean enabled) {
        this.type = type
        this.id = id
        this.variableName = variableName;
        this.enabled = enabled

        if (this.enabled && (!this.type || !this.id)) {
            throw new IllegalArgumentException("Enabled Credential must have a type and an id. (type=${this.type}, id=${this.id}")
        }
    }

    public static Credential getTestData() {
        return new Credential(CredentialType.TEXT, "text-test-credential", null, true)
    }
}
