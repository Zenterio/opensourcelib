package com.zenterio.jenkins.models

import java.util.List;

import groovy.lang.Closure

class PropertySelector implements IPropertySelector {

    private IModel model

    public PropertySelector(IModel model) {
        this.model = model
    }

    @Override
    public IModel getProperty(Class cls = null, Boolean strict = true,
                    Boolean recursive = false,
                    Closure passFilter = { item, result -> true }) {

        Closure propertyPassFilter = { IModel item, result ->
            if (!(item instanceof ModelProperty)) {
                throw new HaltBranchSearchModelException()
            }
            passFilter(item, result)
        }
        return this.model.getChild(cls, strict, recursive,
            propertyPassFilter)
    }

    @Override
    public IModel getProperty(Closure passFilter) {
        return this.getProperty(null, false, true, passFilter)
    }

    @Override
    public List<IModel> getProperties(Class cls, Boolean strict = true,
                    Boolean recursive = false,
                    Closure passFilter = { item, result -> true }) {
        Closure propertyPassFilter = { item, result ->
            if (!(item instanceof ModelProperty)) {
                throw new HaltBranchSearchModelException()
            }
            passFilter(item, result)
        }
        return this.model.getChildren(cls, strict, recursive,
            propertyPassFilter)
    }

    @Override
    public List<IModel> getProperties(Closure passFilter) {
        return this.getProperties(null, false,true, passFilter)
    }

    @Override
    public IModel getParentProperty(Class cls, Boolean strict = true, Boolean recursive = false) {

        return this.model.getParent({ parent, result ->
            parent.getProperty(cls, strict, recursive)
        }).getProperty(cls, strict, recursive)
    }

    @Override
    public List<IModel> getParentProperties(Class cls, Boolean strict = true , Boolean recursive = false) {
        return this.model.getParent({ parent, result ->
            parent.getProperty(cls, strict, recursive)
        }).getProperties(cls, strict, recursive)
    }

    @Override
    public List<IModel> getParentsWithProperty(Class cls, Boolean strict = true, Boolean recursive = false) {
        return this.model.getParents({ parent, result ->
            parent.getProperty(cls, strict, recursive)
        })
    }
}
