package com.zenterio.jenkins.models

/**
 * The Model base class provide an implementation of the IModel
 * Interface, for other classes to inherit from.
 * The BaseModel should not be instantiated directly but instead
 * used as base class for more specific implementations.
 * <p>
 * All manipulation of the core model concepts should be implemented
 * in this class.
 *
 * <p>
 * <strong>Pass-filtering using Closures</strong>
 * <p>
 * For most of the search functions, a Closure can be passed to set conditions
 * for the search (acts like a pass-filter), in addition to using strict class
 * match (not enough being a class through inheritance), or recursive search
 * (the whole model tree).
 * <p>
 * The Closure mechanism offer the following features:
 * The input to the closure is a matched item.
 <pre><code><blockquote>
 { IModel item, ArrayList result -> // do something }
 </blockquote></code></pre>
 * <ul>
 * <li>item: the item (of type IModel) being tested</li>
 * <li>result: list of results collected so far.
 * Items in the list is of type IModel</li>
 * <li>return true: the item will be included in the result</li>
 * <li>return false: the item will be discard from the result</li>
 * <li>throw HaltBranchSearchModelException(), that branch of the tree will
 * not be searched anymore, the current item will not be included.</li>
 * <li>throw HaltTreeSearchModelException() the entire search of the tree
 * will be halted. Any results found so far will be returned.
 * <li>throw InvalidateTreeSearchModelException, the entire search will
 * be halted and no results will be returned. Instead null or empty list
 * depending on context.</li>
 * </ul>
 * <p>
 * <strong>Events</strong>
 * <p>
 * The base model has a set of protected on"Event" methods.
 * <ul>
 * <li>onAddChild(IModel)</li>
 * <li>onRemoveChild(IModel)</li>
 * <li>onSetParent(IModel)</li>
 * <li>onUnsetParent(IModel)</li>
 * </ul>
 * These methods will be called on each action and acts as
 * event handlers. To make use of them in a sub-class, override them using the
 * pattern below:
 <pre><code><blockquote>
 &#064;Override
 protected void onAddChild(IModel child) {
 super.onAddChild(child)
 //do your stuff
 }
 </blockquote></code></pre>
 * Place the call to super before or after your code depending on if you want
 * your action to be performed after or before the rest of the call chain.
 * The methods are protected so they can not be called from outside directly.
 * <p>
 * You can also register event handlers for events on other models.
 * <p>
 * When a parent-child relationship is established, the event order is determined
 * by what method is used to initiate the relationship.
 * <p>
 * If addChild is used, the event order becomes: onAddChild, onSetParent
 * <p>
 * If setParent is used, the event order becomes: onSetParent, onAddChild
 * <p>
 * The onAddChild event is triggered after the child has been added.
 * <p>
 * The onSetParent event is triggered after the parent property has been set.
 *
 */
class BaseModel implements IModel {

    IModel parent
    List<IModel> children

    List<Closure> onAddChildEventListeners
    List<Closure> onRemoveChildEventListeners
    List<Closure> onSetParentEventListeners
    List<Closure> onUnsetParentEventListeners

    public BaseModel() {
        this.parent = null
        this.children = new ArrayList<IModel>()
        this.onAddChildEventListeners = new ArrayList<Closure>()
        this.onRemoveChildEventListeners = new ArrayList<Closure>()
        this.onSetParentEventListeners = new ArrayList<Closure>()
        this.onUnsetParentEventListeners = new ArrayList<Closure>()
    }

    @Override
    public List<IModel> getChildren() {
        return this.children
    }

    @Override
    public List<IModel> getChildren(Class cls, Boolean strict = true,
            Boolean recursive = false, Closure passFilter = { item, result -> true }) {
        return this.findChildren(this, [cls], strict, recursive, passFilter)
    }

    @Override
    public List<IModel> getChildren(List<Class> classes, Boolean strict = true,
            Boolean recursive = false, Closure passFilter = { item, result -> true }) {
        return this.findChildren(this, classes, strict, recursive, passFilter)
    }

    @Override
    public List<IModel> getChildren(Closure passFilter) {
        return this.findChildren(this, [Object], false, true, passFilter)
    }

    /**
     * Wrapper function that handles the tree search-modifying exceptions.
     * @param item          The item being searched
     * @param classes       The list of classes to match against
     * @param strict        Use strict match true|false
     * @param recursive     Use recursive search throughout the tree
     * @param passFilter    Closure that returns true if the child should be
     *                      included in the result or not.
     * @param result        Result list, optional, defaults to new ArrayList.
     * @return              List of matching children.
     */
    protected List<IModel> findChildren(IModel item, List<Class> classes,
            Boolean strict, Boolean recursive, Closure passFilter,
            List<IModel> result = new ArrayList<IModel>()) {
        try {
            this.findChildrenIter(result, item, classes, strict, recursive, passFilter)
        } catch (HaltTreeSearchModelException e) {
            // abort search, but don't modify result
        } catch (InvalidateTreeSearchModelException e) {
            // Invalidate result
            result = new ArrayList<IModel>()
        }
        return result.unique()
    }

    /**
     * Helper function that is called iteratively to search for children that
     * match the provided criteria. The matching children are placed in result.
     * The search is performed depth first.
     * @param result
     * @param item
     * @param classes
     * @param strict
     * @param recursive
     * @param passFilter
     */
    protected void findChildrenIter(List<IModel> result, IModel item, List<Class> classes,
            Boolean strict, Boolean recursive, Closure passFilter) {

        item.children.each { child ->
            try {
                if (passFilter(child, result) && this.matchClass(child, classes,  strict)) {
                    result.add(child)
                }
                if (recursive) {
                    this.findChildrenIter(result, child, classes, strict,
                            recursive, passFilter)
                }
            } catch (HaltBranchSearchModelException e) {
                // do nothing, already prevented children from being processed.
            }
        }
    }


    @Override
    public IModel getChild(Class cls, Boolean strict = false, Boolean recursive = true,
            Closure passFilter = { item, result -> true }) {
        return this.getChild([cls], strict, recursive, passFilter)
    }

    @Override
    public IModel getChild(List<Class> classes, Boolean strict = false,
            Boolean recursive = true, Closure passFilter = { item, result -> true }) {
        IModel result = null
        List<IModel> matches = this.findChildren(this, classes, strict, recursive, passFilter, new FirstResultList())
        if (matches.size() > 0) {
            result = matches[0]
        }
        return result
    }

    @Override
    public IModel getChild(Closure passFilter) {
        return this.getChild([Object], false, true, passFilter)
    }

    @Override
    public IModel getParent() {
        return this.parent
    }

    @Override
    public IModel getParent(Class cls, Boolean strict = true,
            Closure passFilter = { item, result -> true }) {
        return this.findParent(this, [cls], strict, passFilter)
    }

    @Override
    public IModel getParent(List<Class> classes, Boolean strict = true,
            Closure passFilter = { item, result -> true }) {
        return this.findParent(this, classes, strict, passFilter)
    }

    @Override
    public IModel getParent(Closure passFilter) {
        return this.findParent(this, null, false, passFilter)
    }

    @Override
    public List<IModel> getParents(Class cls = null, Boolean strict = true,
            Closure passFilter = { item, result -> true }) {
        return this.findParents(this, [cls], strict, passFilter)
    }

    @Override
    public List<IModel> getParents(List<Class> classes, Boolean strict = true,
            Closure passFilter = { item, result -> true }) {
        return this.findParents(this, classes, strict, passFilter)
    }

    @Override
    public List<IModel> getParents(Closure passFilter) {
        return this.findParents(this, null, false, passFilter)
    }

    /**
     * Add a child node to the model tree. The child is not added
     * if it already exist in the list or if it is null.
     * @param child
     * @return the child being added
     */
    @Override
    public IModel addChild(IModel child) {

        if (child != null && !this.children.contains(child)) {
            this.children.add(child)
            this.onAddChild(child)
            child.setParent(this)
        }
        return child
    }


    /**
     * Similar behavior to addChild with the difference that it
     * returns the node being added to instead of the child being added.
     * This difference is to make it convenient and safe to use add
     * in with-blocks to provide a more DSL like look-and-feel.
     *
     * @param child
     * @return the node being added to.
     */
    @Override
    public IModel add(IModel child) {
        this.addChild(child)
        return this
    }

    @Override
    public String toString() {
        return super.toString()
    }

    public String toDebugString(int indent=0) {
        return (" " * indent) + super.toString() + "\n" +
                this.children.collect({ IModel it ->
                    it.toDebugString(indent + 2)
                }).join("\n")
    }

    protected IModel findParent(IModel item, List<Class> classes, Boolean strict,
            Closure passFilter) {
        IModel result = null
        List<IModel> matches = this.getParents(classes, strict, passFilter)
        if (matches.size > 0) {
            result = matches[0]
        }
        return result
    }

    protected List<IModel> findParents(IModel item, List<Class> classes,
            Boolean strict, Closure passFilter) {
        List<IModel> result = new ArrayList<IModel>()
        try {
            this.findParentsIter(result, item, classes, strict, passFilter)
        } catch (HaltBranchSearchModelException e) {
            // abort search, but don't modify result
        } catch (HaltTreeSearchModelException e) {
            // abort search, but don't modify result
        } catch (InvalidateTreeSearchModelException e) {
            // Invalidate result
            result = new ArrayList<IModel>()
        }
        return result
    }

    protected void findParentsIter(List<IModel> result, IModel item,
            List<Class> classes, Boolean strict, Closure passFilter) {
        IModel parent = item.parent
        if (parent != null) {
            if (passFilter(parent, result) && this.matchClass(parent, classes, strict)) {
                result.add(parent)
            }
            this.findParentsIter(result, parent, classes, strict, passFilter)
        }
    }

    protected Boolean matchClass(IModel item, List<Class> classes, Boolean strict) {
        Boolean match = false

        if (classes == null || classes.size == 0) {
            match = true
        } else {
            for (Class cls in classes) {
                if (cls == null) {
                    match = true
                    break
                }
                if (!strict && (item in cls)) {
                    match = true
                    break
                }
                else if (strict && (item.class == cls)) {
                    match = true
                    break
                }
            }
        }
        return match
    }

    @Override
    public IModel leftShift(IModel other) {
        this.addChild(other)
        return other
    }

    @Override
    public IModel getAt(Class cls) {
        return this.getChild(cls)
    }

    /**
     * Sets the parent
     * @param parent    The parent to be assigned
     * @return          the parent assigned
     */
    @Override
    public IModel setParent(IModel parent) {
        if (this.parent != parent) {
            this.unsetParent()
            this.setParentProperty(parent)
            this.onSetParent(parent)
            parent.addChild(this)
        }
        return this.parent
    }

    /**
     * Helper method to be able to set the parent field cleanly from sub-class.
     * @param parent
     */
    protected void setParentProperty(IModel parent) {
        this.@parent = parent
    }

    /**
     * Sets the parent to null
     * @param onParent 	the parent to unset (optional).
     * 					If used and it does not match the current parent, the parent
     * 					will not be unset.
     * @return the previous parent, or null if onParent did not match current parent
     */
    @Override
    public IModel unsetParent(IModel onParent = null) {
        IModel oldParent = this.parent
        if (this.parent != null && (onParent == null || onParent == oldParent)) {
            this.parent = null
            this.onUnsetParent(oldParent)
            oldParent.removeChild(this)
            return oldParent
        }
        return null
    }

    /**
     * Removes the specified child and returns it.
     * @param child the child to be removed
     * @return the child removed, null if not existing
     */
    @Override
    public IModel removeChild(IModel child) {
        Boolean result = this.children.remove(child)
        if (result) {
            this.onRemoveChild(child)
            child.unsetParent(this)
        }
        return (result) ? child : null
    }

    /**
     * Event handler for addChild(). Override in sub class to have effect.
     *
     * @param child  The child item being added.
     */
    protected void onAddChild(IModel child) {
        this.onAddChildEventListeners.each({ handler ->
            handler(child, this)
        })
    }

    /**
     * Event handler for removeChild(). Override in sub class to have effect.
     *
     * @param child  The child item being removed.
     */
    protected void onRemoveChild(IModel child) {
        this.onRemoveChildEventListeners.each({ handler ->
            handler(child, this)
        })
    }

    /**
     * Event handler for setParent(). Override in sub class to have effect.
     * @param parent    The parent being set.
     */
    protected void onSetParent(IModel parent) {
        this.onSetParentEventListeners.each({ handler ->
            handler(parent, this)
        })
    }

    /**
     * Event handler for unsetParent(). Override in sub class to have effect.
     * @param oldParent The old parent being unset.
     */
    protected void onUnsetParent(IModel oldParent) {
        this.onUnsetParentEventListeners.each({ handler ->
            handler(oldParent, this)
        })
    }

    /**
     * The handler will be called with (child, model) when a child is added.
     * @param handler
     * @return the handler registered
     */
    public Closure regOnAddChildEventHandler(Closure handler) {
        this.onAddChildEventListeners.add(handler)
        return handler
    }

    /**
     * The handler will be called with (child, model) when a child is removed.
     * @param handler
     * @return the handler registered
     */
    public Closure regOnRemoveChildEventHandler(Closure handler) {
        this.onRemoveChildEventListeners.add(handler)
        return handler
    }

    /**
     * The handler will be called with (parent, model) when a parent is set.
     * @param handler
     * @return the handler registered
     */
    public Closure regOnSetParentEventHandler(Closure handler) {
        this.onSetParentEventListeners.add(handler)
        return handler
    }

    /**
     * The handler will be called with (parent, model) when the parent is unset.
     * @param handler
     * @return the handler registered
     */
    public Closure regOnUnsetParentEventHandler(Closure handler) {
        this.onUnsetParentEventListeners.add(handler)
        return handler
    }

    /**
     * Removes onAddChild event handler
     * @param handler
     * @return the handler unregistered
     */
    public Closure unregOnAddChildEventHandler(Closure handler) {
        this.onAddChildEventListeners.remove(handler)
        return handler
    }

    /**
     * Removes onRemoveChild event handler
     * @param handler
     * @return the handler unregistered
     */
    public Closure unregOnRemoveChildEventHandler(Closure handler) {
        this.onRemoveChildEventListeners.remove(handler)
        return handler
    }

    /**
     * Removes onSetParent event handler
     * @param handler
     * @return the handler unregistered
     */
    public Closure unregOnSetParentEventHandler(Closure handler) {
        this.onSetParentEventListeners.remove(handler)
        return handler
    }

    /**
     * Removes onUnsetParent event handler
     * @param handler
     * @return the handler unregistered
     */
    public Closure unregOnUnsetParentEventHandler(Closure handler) {
        this.onUnsetParentEventListeners.remove(handler)
        return handler
    }

    class FirstResultList extends ArrayList<IModel> {

        @Override
        public boolean add(IModel item) {
            super.add(item)
            throw new HaltTreeSearchModelException()
            return true
        }
    }
}
