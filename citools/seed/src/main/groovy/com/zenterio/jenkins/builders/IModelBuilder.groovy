package com.zenterio.jenkins.builders

import com.zenterio.jenkins.models.IModel

/**
 * Helper classes (aka "Builders") should implement this interface.
 * Any custom parameters needed to build the model should be passed
 * via the constructor of the Builder implementation.
 */
interface IModelBuilder {

    public IModel build();
}
