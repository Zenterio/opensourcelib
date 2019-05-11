package com.zenterio.jenkins.models


interface IPropertySelector {

    public IModel getProperty(Class cls);
    public IModel getProperty(Class cls, Boolean strict);
    public IModel getProperty(Class cls, Boolean strict, Boolean recursive);
    public IModel getProperty(Class cls, Boolean strict, Boolean recursive,
                              Closure passFilter);
    public IModel getProperty(Closure passFilter);

    public List<IModel> getProperties(Class cls);
    public List<IModel> getProperties(Class cls, Boolean strict);
    public List<IModel> getProperties(Class cls, Boolean strict,
                                      Boolean recursive);
    public List<IModel> getProperties(Class cls, Boolean strict,
                                      Boolean recursive, Closure passFilter);
    public List<IModel> getProperties(Closure passFilter);

    /**
     * Finds the closest parent with a matching property and returns the first
     * property that matches.
     * @param cls           The class/type of property to match against.
     * @param strict        Use strict matching (exact class) if true.
     * @param recursive     Search properties of properties if set to true.
     * @return Returns PropertyModel of parent
     */
    public IModel getParentProperty(Class cls, Boolean strict, Boolean recursive);
    public IModel getParentProperty(Class cls, Boolean strict);
    public IModel getParentProperty(Class cls);

    /**
     * Finds the closest parent with a matching property and returns all properties
     * that matches.
     * @param cls           The class/type of property to match against.
     * @param strict        Use strict matching (exact class) if true.
     * @param recursive     Search properties of properties if set to true.
     * @return Returns list of properties of parent
     */
    public List<IModel> getParentProperties(Class cls, Boolean strict, Boolean recursive);
    public List<IModel> getParentProperties(Class cls, Boolean strict);
    public List<IModel> getParentProperties(Class cls);

    /**
     * Returns all parents with at least one matching property.
     * @param cls           The class/type of property to match against.
     * @param strict        The class/type of property to match against.
     * @param recursive     Search properties of properties if set to true.
     * @return Returns list of parents that have matching property.
     */
    public List<IModel> getParentsWithProperty(Class cls, Boolean strict, Boolean recursive);
    public List<IModel> getParentsWithProperty(Class cls, Boolean strict);
    public List<IModel> getParentsWithProperty(Class cls);

}
