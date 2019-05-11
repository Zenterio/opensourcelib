package com.zenterio.jenkins.models

interface IModel {

    public List<IModel> getChildren()
    public List<IModel> getChildren(Class cls, Boolean strict,
        Boolean recursive, Closure passFilter)
    public List<IModel> getChildren(List<Class> classes, Boolean strict,
        Boolean recursive, Closure passFilter)
    public List<IModel> getChildren(Closure passFilter)

    public IModel getChild(Class cls, Boolean strict, Boolean recursive,
        Closure passFilter)
    public IModel getChild(List<Class> classes, Boolean strict, Boolean recursive,
        Closure passFilter)
    public IModel getChild(Closure passFilter)

    public List<IModel> getParents()
    public List<IModel> getParents(Class cls, Boolean strict,
        Closure passFilter)
    public List<IModel> getParents(List<Class> classes, Boolean strict,
        Closure passFilter)
    public List<IModel> getParents(Closure passFilter)

    public IModel getParent()
    public IModel getParent(Class cls, Boolean strict, Closure passFilter)
    public IModel getParent(List<Class> classes, Boolean strict, Closure passFilter)
    public IModel getParent(Closure passFilter)

    public IModel setParent(IModel parent)
    public IModel unsetParent()

    public IModel addChild(IModel child)
    public IModel add(IModel child)
    public IModel leftShift(IModel other)
    public IModel getAt(Class cls)

    public IModel removeChild(IModel child)

    public String toDebugString()

    public Closure regOnAddChildEventHandler(Closure handler)
    public Closure regOnRemoveChildEventHandler(Closure handler)
    public Closure regOnSetParentEventHandler(Closure handler)
    public Closure regOnUnsetParentEventHandler(Closure handler)

    public Closure unregOnAddChildEventHandler(Closure handler)
    public Closure unregOnRemoveChildEventHandler(Closure handler)
    public Closure unregOnSetParentEventHandler(Closure handler)
    public Closure unregOnUnsetParentEventHandler(Closure handler)
}
