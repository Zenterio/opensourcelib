package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.dispatcher.HaltDispatchException
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty

class JobBuildFlowForkGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) throws HaltDispatchException {
        // Currently does nothing
    }

}
