package com.zenterio.jenkins.models.job.flowdsl

class BuildFlowDslJoinNodeTest extends GroovyTestCase {

    BuildFlowDslNode root

    @Override
    void setUp() throws Exception {
        this.root = new BuildFlowDslNode("root")
    }

    void testJoinCanBeOnlyChild() {
        BuildFlowDslJoinNode join = new BuildFlowDslJoinNode()
        this.root << join
    }

    void testJoinNodeThrowsExceptionIfParentHasOtherDslNodeChild() {
        BuildFlowDslJoinNode join = new BuildFlowDslJoinNode()
        this.root << new BuildFlowDslNode("N")
        shouldFail(BuildFlowDslJoinNode.BuildFlowDslJoinNodeSiblingException, { this.root << join })
    }

    void testJoinNodeThrowsExceptionIfSiblingIsAdded() {
        this.root << new BuildFlowDslJoinNode()
        shouldFail(BuildFlowDslJoinNode.BuildFlowDslJoinNodeSiblingException,{
            this.root << new BuildFlowDslNode("N")
        })
    }
}

