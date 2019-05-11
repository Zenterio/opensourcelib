package com.zenterio.jenkins.generators

import com.zenterio.jenkins.dispatcher.HaltDispatchException
import com.zenterio.jenkins.models.ModelEntity


interface IEntityGenerator extends IGenerator {

    public void generate(ModelEntity model) throws HaltDispatchException
}
