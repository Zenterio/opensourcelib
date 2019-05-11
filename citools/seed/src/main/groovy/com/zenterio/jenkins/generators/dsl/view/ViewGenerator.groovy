package com.zenterio.jenkins.generators.dsl.view

import com.zenterio.jenkins.generators.IEntityGenerator
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.view.ViewNameModel

import groovy.util.logging.*


@Log
class ViewGenerator implements IEntityGenerator {

    public Closure viewCreator

    public ViewGenerator(Closure viewCreator){
        this.viewCreator = viewCreator
    }

    public void generate(ModelEntity model) {
        String name = model.getChild(ViewNameModel).name
        model.entity = this.viewCreator(name)
        log.finer("View Generated (entity=${model.entity?.class?.name})")
    }
}
