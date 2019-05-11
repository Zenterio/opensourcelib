package com.zenterio.jenkins.dispatcher

import com.zenterio.jenkins.generators.IEntityGenerator
import com.zenterio.jenkins.generators.IGenerator
import com.zenterio.jenkins.generators.IPropertyGenerator

import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.ModelProperty
import groovy.util.logging.*


/**
 * This implementation of the dispatcher uses loose class match
 * to find which generator to apply, if any, on contrast to the exact class
 * match done in Dispatcher class.
 * <p>
 * Loose class match means that if the models class is not registered, it
 * will try its super class. If that class is not registered, it will try that
 * class' super class, and so on until a match is found, or reaching the root
 * class.
 * <p>
 * See also {@link com.zenteri.jenkins.dispatcher.ExactMatchDispatcher}
 */
@Log
class LooseMatchDispatcher extends ExactMatchDispatcher {

    /**
     * Constructor
     *
     * @param generatePropertyForNullEntity set to true if property generators
     * 										and property models should be applied
     * 										to null-entities; default=false.
     */
    public LooseMatchDispatcher(Boolean generatePropertyForNullEntity=false) {
        super(generatePropertyForNullEntity)
    }


    /**
     * Get the generator registered for the provided model(class),
     * using loose match.
     *
     * @param model The model for which to get the associated generator
     * @return the associated generator
     */
    @Override
    public IGenerator getGenerator(IModel model) {
        Class cls = model.class
        IGenerator g = null
        while (cls != null) {
            g = this.generators.get(cls.name)
            if (g) {
                break
            }
            cls = cls.superclass
        }
        log.finer("Get Generator (model=${model.class.name}, generator=${g?.class?.name})")
        return g
    }
}
