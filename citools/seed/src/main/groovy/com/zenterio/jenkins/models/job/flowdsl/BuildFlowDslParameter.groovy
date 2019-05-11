package com.zenterio.jenkins.models.job.flowdsl


class BuildFlowDslParameter {

    String name
    String value

    public BuildFlowDslParameter(String name, String value) {
        super();
        this.name = name;
        this.value = value;
    }

    @Override
    public String toString() {
        return "${this.name}: ${this.value}"
    }
}
