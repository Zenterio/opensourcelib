package com.zenterio.jenkins.models.job.flowdsl

import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.JoinModel


class BuildFlowDslJoinNode extends JoinModel {

    static final List<Class> RESTRICTED_CLASSES = [
        BuildFlowDslNode,
        BuildFlowDslForkNode,
        BuildFlowDslJoinNode
    ]
    Boolean hasBeenRendered
    Closure onAddChildEventHandler

    public BuildFlowDslJoinNode() {
        this.hasBeenRendered = false
        BuildFlowDslJoinNode self = this
        this.onAddChildEventHandler = { IModel childAdded, IModel onParent ->
            if (childAdded != self) {
                for (Class cls in RESTRICTED_CLASSES) {
                    if (childAdded in cls) {
                        throw new BuildFlowDslJoinNodeSiblingException()
                    }
                }
            }
        }
    }

    @Override
    protected void onSetParent(IModel parent) {
        super.onSetParent(parent)
        if (parent.getChildren(RESTRICTED_CLASSES).size > 1) {
            throw new BuildFlowDslJoinNodeSiblingException()
        }
        parent.regOnAddChildEventHandler(this.onAddChildEventHandler)
    }

    @Override
    protected void onUnsetParent(IModel parent) {
        super.onUnsetParent(parent)
        parent.unregOnAddChildEventHandler(this.onAddChildEventHandler)
    }

    public class BuildFlowDslJoinNodeSiblingException extends Exception {
        public BuildFlowDslJoinNodeSiblingException() {
            super("BuildFlowDslJoinNode can not have siblings")
        }
    }
}
