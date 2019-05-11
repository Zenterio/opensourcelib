package com.zenterio.jenkins.models.job.flowdsl

import com.zenterio.jenkins.models.BaseModel
import com.zenterio.jenkins.models.IModel


class BuildFlowDslNode extends BaseModel {

    String jobName
    ArrayList<BuildFlowDslParameter> extraParameters

    public BuildFlowDslNode(String jobName,
            List<BuildFlowDslParameter> extraParameters = new ArrayList<BuildFlowDslParameter>()) {
        this.jobName = jobName
        this.extraParameters = extraParameters
    }

    @Override
    public String toDebugString(int indent=0) {
        return (" " * indent) + super.toString() + " - " + this.jobName + "\n" +
                this.children.collect({ IModel it ->
                    it.toDebugString(indent + 2)
                }).join("\n")
    }
}
