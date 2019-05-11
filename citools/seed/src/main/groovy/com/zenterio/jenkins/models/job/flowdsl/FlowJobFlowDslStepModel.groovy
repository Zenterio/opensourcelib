package com.zenterio.jenkins.models.job.flowdsl

import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.IPropertySelector
import com.zenterio.jenkins.models.job.BaseJobModel
import com.zenterio.jenkins.models.job.FlowJobModel
import com.zenterio.jenkins.models.job.JobBuildFlowForkModel
import com.zenterio.jenkins.models.job.JobBuildFlowJoinModel
import com.zenterio.jenkins.models.job.JobBuildStepModel
import com.zenterio.jenkins.models.job.JobNameModel


class FlowJobFlowDslStepModel extends JobBuildStepModel {

    protected BuildFlowDslRenderer dsl
    Class jobPassFilter
    Class joinPassFilter
    Class forkPassFilter
    Closure passFilter
    List<Class> acceptedClasses
    HashMap<IModel, IModel> convertedModels

    public FlowJobFlowDslStepModel(BuildFlowDslParameter[] callParameters,
            BuildFlowDslVariable[] variables=[],
            jobPassFilter=BaseJobModel,
            forkPassFilter=JobBuildFlowForkModel,
            joinPassFilter=JobBuildFlowJoinModel) {
        super("")
        this.dsl = new BuildFlowDslRenderer(callParameters, variables)
        this.jobPassFilter = jobPassFilter
        this.joinPassFilter = joinPassFilter
        this.forkPassFilter = forkPassFilter
        this.convertedModels = new HashMap<IModel,IModel>()

        // Filter out all models with the ExcludeFromFlow property.
        this.passFilter = { IPropertySelector item, result ->
            (! (item.getProperty(JobBuildFlowDslExcludeFromFlowModel, false, true)))
        }

        this.acceptedClasses = [
            this.jobPassFilter,
            this.joinPassFilter,
            this.forkPassFilter
        ]
    }

    @Override
    public String getScript() {
        FlowJobModel job = this.getParent(FlowJobModel, false)
        BuildFlowDslNode root = this.buildNodeTree(job)
        return this.dsl.render(root)
    }

    /**
     * The Node tree is a reduced tree of the model tree,
     * where job models represented as nodes and their names
     * stored in each node. All other entities and properties
     * are ignored except custom build flow DSL parameters and flow models .
     *
     * @param model
     * @return node representation of the model and its children
     */
    protected IModel buildNodeTree(IModel model) {

        if (this.convertedModels.containsKey(model)) {
            return this.convertedModels[model]
        }

        IModel proxyNode = null
        IModel resultNode = this.createNode(model)
        List<IModel> children = this.getChildren(model)
        this.convertedModels[model] = resultNode

        /*
         * Inject a fork model if needed
         */
        if (!(model in this.forkPassFilter) && (children.size > 1)) {
            proxyNode = this.buildForkNode()
            resultNode.add(proxyNode)
        } else {
            proxyNode = resultNode
        }

        /* We use the proxy node to allow for injecting a fork node */
        children.each { IModel child -> proxyNode.addChild(this.buildNodeTree(child)) }

        return resultNode
    }


    /**
     *  Get all direct children (recursive=false) that are of the specified classes
     *  including sub-class (strict=false).
     *
     *  @param model
     */
    protected List<IModel> getChildren(IModel model) {
        return model.getChildren(this.acceptedClasses, false, false, this.passFilter)
    }

    protected IModel createNode(IModel model) {
        if (model in this.joinPassFilter) {
            return this.buildJoinNode()
        } else if (model in this.forkPassFilter) {
            return this.buildForkNode()
        } else {
            return this.buildJobNode(model)
        }
    }

    protected BuildFlowDslNode buildJobNode(IModel model) {
        String jobName = model[JobNameModel]?.name
        return new BuildFlowDslNode(jobName, this.getCustomParams(model))
    }

    protected BuildFlowDslJoinNode buildJoinNode() {
        return new BuildFlowDslJoinNode()
    }

    protected BuildFlowDslForkNode buildForkNode() {
        return new BuildFlowDslForkNode()
    }

    protected List<BuildFlowDslParameter> getCustomParams(IModel model) {
        List<BuildFlowDslParameter> result = new ArrayList<BuildFlowDslParameter>()
        model.getProperties(JobBuildFlowDslParameterModel, false).each({ JobBuildFlowDslParameterModel param ->
            result.add(new BuildFlowDslParameter(param.parameterName, param.parameterValue))
        })
        return result
    }

}
