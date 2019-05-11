package com.zenterio.jenkins.generators

import com.zenterio.jenkins.dispatcher.HaltDispatchException
import com.zenterio.jenkins.models.ModelProperty


interface IPropertyGenerator extends IGenerator {

    public void generate(ModelProperty model, Object entity) throws HaltDispatchException
}
