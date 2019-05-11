package com.zenterio.jenkins.models.job.flowdsl

import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobBuildFlowForkModel
import com.zenterio.jenkins.models.job.JobBuildFlowJoinModel
import com.zenterio.jenkins.models.job.JobModel
import com.zenterio.jenkins.models.job.JobNameModel

class FlowJobFlowDslStepModelBuildNodeTreeTest extends GroovyTestCase {

    FlowJobFlowDslStepModel step

    @Override
    void setUp() throws Exception {
        this.step = new FlowJobFlowDslStepModel(new BuildFlowDslParameter[0])
    }

    protected JobModel getJob(String name) {
        JobModel job = new JobModel()
        job << new JobNameModel(name)
        return job
    }

    protected JobBuildFlowJoinModel getJoin() {
        return new JobBuildFlowJoinModel()
    }

    protected JobBuildFlowForkModel getFork() {
        return new JobBuildFlowForkModel()
    }

    public void testSingleJobNode() {
        IModel node = this.step.buildNodeTree(this.getJob("NAME"))
        assert node in BuildFlowDslNode
        assert node.children.size == 0
    }

    public void testSingleForkNode() {
        IModel node = this.step.buildNodeTree(this.getFork())
        assert node in BuildFlowDslForkNode
    }

    public void testSingleJoinNode() {
        IModel node = this.step.buildNodeTree(this.getJoin())
        assert node in BuildFlowDslJoinNode
    }

    public void testForkIsInjectedIfMultipleChildren() {
        IModel job = this.getJob("root")
        job << this.getJob("A1")
        job << this.getJob("A2")
        IModel node = this.step.buildNodeTree(job)
        assert node in BuildFlowDslNode
        assert node.children.size == 1
        assert node.children[0] in BuildFlowDslForkNode
        IModel fork = node.children[0]
        assert fork.children.size == 2
        assert fork.children[0] in BuildFlowDslNode
    }

    public void testForkIsNotInjectedIfSingleChild() {
        IModel job = this.getJob("root")
        job << this.getJob("A") << this.getJob("B")
        IModel node = this.step.buildNodeTree(job)

        assert node in BuildFlowDslNode
        assert node.children.size == 1
        assert node.children[0] in BuildFlowDslNode
        IModel child = node.children[0]
        assert child.children.size == 1
        assert child.children[0] in BuildFlowDslNode
    }

    public void testExtraForkIsNotInjectedIfForkHasMultipleChildren() {
        IModel jobFork = this.getFork()
        jobFork << this.getJob("A1")
        jobFork << this.getJob("A2")
        IModel node = this.step.buildNodeTree(jobFork)
        assert node in BuildFlowDslForkNode
        assert node.children.size == 2
        assert node.children[0] in BuildFlowDslNode
    }

    /**
     * Test that join is preserved as a single instance.
     *
     * Input:
     *    fork
     *    /  \
     *   A1  A2
     *    \  /
     *    join
     *      |
     *      B
     *
     * Should be translated to:
     *    fork
     *    /  \
     *   A1  A2
     *    \  /
     *    join
     *      |
     *      B
     */
    public void testJoinIsPreservedAsSingleInstance( ) {
        IModel jobFork = this.getFork()
        IModel jobJoin = this.getJoin()
        jobFork << this.getJob("A1") << jobJoin << this.getJob("B")
        jobFork << this.getJob("A2") << jobJoin

        IModel nodeFork = this.step.buildNodeTree(jobFork)
        assert nodeFork.children.size == 2
        IModel nodeJoin = nodeFork.children[0].children[0]
        assert nodeJoin == nodeFork.children[1].children[0]
        assert nodeJoin.children.size == 1
    }

}

