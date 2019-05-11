package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.dispatcher.HaltDispatchException
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty

class JobBuildFlowJoinGenerator implements IPropertyGenerator {

    List<ModelProperty> dispatchedModels = new ArrayList<ModelProperty>()

    @Override
    public void generate(ModelProperty model, Object entity) throws HaltDispatchException {
        /*
         * Add model to list of dispatched models to ensure that the join's children are only dispatched once.
         * If the particular join has been dispatched before, throw a HaltDispatchException to prevent its children
         * from being dispatched again.
         */
        if (this.dispatchedModels.contains(model)) {
            throw new HaltDispatchException(model)
        } else {
            this.dispatchedModels.add(model)
        }
    }

}
