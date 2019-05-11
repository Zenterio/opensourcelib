package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class JobArtifactModel extends ModelProperty {

    final String pattern
    final Boolean fingerprinting

    public JobArtifactModel(String pattern, Boolean fingerprinting) {
        super()
        this.pattern = pattern
        this.fingerprinting = fingerprinting
    }

    public String getPattern() {
        return this.pattern
    }
}
