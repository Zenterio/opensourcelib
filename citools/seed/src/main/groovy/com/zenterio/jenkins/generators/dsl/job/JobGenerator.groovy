package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IEntityGenerator
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.job.JobNameModel

import groovy.util.logging.*


@Log
class JobGenerator implements IEntityGenerator {

    public Closure jobCreator;

    public JobGenerator(Closure jobCreator){
        this.jobCreator = jobCreator;
    }

    public void generate(ModelEntity model) {
        String name = model.getChild(JobNameModel).name
        model.entity = this.jobCreator(name)
        log.finer("Job Generated (entity=${model.entity?.class?.name})")
    }
}
