package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator;
import com.zenterio.jenkins.models.ModelProperty


class JobTimeStampGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        if (model.enabled) {
            entity.with {
                wrappers {
                    timestamps()
                }
            }
        }

    }

}
