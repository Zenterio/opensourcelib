package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


/**
 * The purpose of this class is to create an abstraction layer separating
 * Product related configuration classes from other classes dependent
 * on BaseStructureConfig.
 */
@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
abstract class BaseProduct extends BaseCompilationStructureConfig {

    /**
     * Default constructor
     */
    public BaseProduct() {
        super()
    }

    /**
     * Copy constructor
     * @param other
     */
    public BaseProduct(BaseProduct other) {
        super(other)
    }

    /**
     * Returns the products origin.
     * @return the products origin.
     * TODO: Work-around that should be removed. (ZMT-2048)
     *  It exists because there
     *  are bidirectional dependencies between origin and product that
     *  should not be there in the first place.
     */
    abstract public Origin getOrigin();
}
