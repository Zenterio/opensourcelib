package com.zenterio.jenkins.models

/**
 * The purpose of the join model is to make it possible to not only model trees but also
 * model more complex structures such as directional acyclic graphs (if child and parent relationship
 * is considered different directions).
 * No check is done to prevent cyclic dependencies.
 */
class JoinModel extends ModelProperty {

    List<IModel> extraParents

    public JoinModel() {
        super()
        this.extraParents = new ArrayList<IModel>()
    }

    /**
     * Sets the parent. If parent already set, the parent is added as extra parent.
     * @param parent    The parent to be assigned
     * @return          the parent assigned
     */
    @Override
    public IModel setParent(IModel parent) {
        if (this.parent == null) {
            super.setParent(parent)
        } else {
            if (this.parent != parent && !this.extraParents.contains(parent)) {
                this.extraParents.add(parent)
                this.onSetParent(parent)
                parent.addChild(this)
            }
        }
        return this.parent
    }

    /**
     * Unsets the parent
     * @param onParent 	the parent to unset (optional).
     * 					If used and it does not match the current parent, the parent
     * 					will not be unset.
     * @return the previous parent or null if parent wasn't unset.
     */
    @Override
    public IModel unsetParent(IModel onParent = null) {
        IModel oldParent = this.parent
        if (this.parent != null && (onParent == null || onParent == oldParent)) {
            this.parent = null
            this.onUnsetParent(oldParent)
            oldParent.removeChild(this)
            return oldParent
        } else if (onParent != null) {
            if (this.extraParents.remove(onParent)) {
                this.onUnsetParent(onParent)
                onParent.removeChild(this)
                return onParent
            }
        }
        return null
    }
}
