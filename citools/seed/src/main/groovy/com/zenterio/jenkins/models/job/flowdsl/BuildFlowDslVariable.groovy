package com.zenterio.jenkins.models.job.flowdsl


class BuildFlowDslVariable {

    String name
    String value

    public BuildFlowDslVariable(String name, String value) {
        super();
        this.name = name;
        this.value = value;
    }

    @Override
    public String toString() {
        return "${this.name}: ${this.value}"
    }
}
