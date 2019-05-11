package com.zenterio.jenkins.dispatcher

import com.zenterio.jenkins.generators.IEntityGenerator
import com.zenterio.jenkins.generators.IGenerator
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.ModelProperty

import groovy.util.logging.*


/**
 * See also {@link com.zenteri.jenkins.dispatcher.IDispatcher}
 * <p>
 * This implementation of the dispatcher uses exact class match
 * to find which generator to apply, if any.
 * <p>
 * When dispatching property models, it will search the parent path until
 * it finds an entity model to get hold of the entity object to apply it on.
 * This allows for modifying properties on properties.
 * <p>
 * The model is dispatched in a depth first recursive pattern. Hence, ensuring
 * that any child node will be dispatched after its parent. It also has the
 * effect that any child and grand-child is dispatched before siblings.
 */
@Log
class ExactMatchDispatcher implements IDispatcher {

    /**
     * Stores the mapping between classes and generators.
     */
    protected HashMap<String, IGenerator> generators

    /**
     * Flag, if entity generators/models should be
     * applied to null-entities. Defaults to false
     * if not set in the constructor.
     */
    protected Boolean generatePropertyForNullEntity

    /**
     * Constructor
     *
     * @param generatePropertyForNullEntity set to true if property generators
     * 										and property models should be applied
     * 										to null-entities; default=false.
     */
    public ExactMatchDispatcher(Boolean generatePropertyForNullEntity=false) {
        this.generators = new HashMap<String, IGenerator>()
        this.generatePropertyForNullEntity = generatePropertyForNullEntity
    }

    /**
     * Dispatches a model entity.
     *
     * Applies the associated IEntityGenerator on the model
     * and recursively dispatches the models children.
     *
     * @param model The model entity to be dispatched.
     */
    @Override
    public void dispatch(ModelEntity model) {
        try {
            IEntityGenerator g = this.getGenerator(model)
            log.finer("Dispatch (entity=${model.class.name}, generator=${g?.class?.name})")
            g?.generate(model)
            this.dispatchChildren(model)
        } catch (HaltDispatchException e) {
            // Expected to be thrown from generate, in which case we do nothing
        }
    }

    /**
     * Dispatches a model property.
     *
     * A model property is associated with a model entity that is expected
     * to hold the entity that the property is applied on using the registered
     * IPropertyGenerator. The dispatcher do a non-strict recursive search of
     * the models parent nodes until it finds a model that inherits from
     * ModelEntity, to acquire the actual entity used in the operation.
     * <p>
     * This mechanism allows for properties on properties on entities, and it
     * is still the entity being modified. This is an intentional pattern.
     *
     * After applying any matching IPropertyGenerator, it recursively dispatches
     * the models children.
     *
     * @param model The model to be dispatched.
     */
    @Override
    public void dispatch(ModelProperty model) {
        ModelEntity parent = model.getParent(ModelEntity, false)
        Object e = parent?.entity
        Boolean dispatchChildren = true
        IPropertyGenerator g = this.getGenerator(model)
        log.finer("Dispatch (property=${model.class.name}, entity=${e?.class?.name}, generator=${g?.class?.name})")

        if ((e != null) || this.generatePropertyForNullEntity) {
            try {
                g?.generate(model, e)
            } catch (HaltDispatchException halt) {
                dispatchChildren = false
            } catch (all) {
                log.severe("Failed to generate (property=${model.class.name}, entity=${e?.class?.name}, generator=${g?.class?.name})")
                throw all
            }
        } else {
            log.warning("Dispatch Property model for null entity not generated (property=${model.class.name}, entity=${e?.class?.name}, generator=${g?.class?.name})")
        }
        if (dispatchChildren) {
            this.dispatchChildren(model)
        }
    }

    /**
     * Dispatches the provided models children.
     *
     * @param model The model who's children should be dispatched.
     */
    protected void dispatchChildren(IModel model) {
        model.children.each { child ->
            this.dispatch(child)
        }
    }

    /**
     * Get the generator registered for the provided model(class).
     *
     * @param model The model for which to get the associated generator
     * @return the associated generator
     */
    @Override
    public IGenerator getGenerator(IModel model) {
        IGenerator g = this.generators.get(model.class.name)
        log.finer("Get Generator (model=${model.class.name}, generator=${g?.class?.name})")
        return g
    }

    /**
     * Registered the Generator to be applied on the provided class when
     * dispatching a model tree.
     *
     * @param cls
     * @param generator
     */
    @Override
    public void registerGenerator(Class cls, IGenerator generator) {
        log.config("Added generator (Class=${cls.name}, Generator=${generator.class.name})")
        this.generators.put(cls.name, generator)
    }

    /**
     * Similar to registerGenerator.
     *
     * With the addition that it returns the dispatcher itself to make it convenient and
     * safe to use reg in with-blocks, to provide a more DSL like look-and-feel.
     * See class description for code example on use.
     *
     * @param cls
     * @param generator
     * @return returns the dispatcher
     */
    @Override
    public IDispatcher reg(Class cls, IGenerator generator) {
        this.registerGenerator(cls, generator)
        return this
    }
}
