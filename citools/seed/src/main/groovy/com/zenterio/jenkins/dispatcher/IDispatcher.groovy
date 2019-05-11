package com.zenterio.jenkins.dispatcher

import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.generators.IGenerator
import com.zenterio.jenkins.models.IModel

/**
 * The dispatcher traverses the model tree passed to it,
 * and applies any registered generator associated with
 * the model.
 *
 * The preferred way of configuring the dispatcher, is to use
 * "reg", the synonym method to registerGenerator, in a with-block.
 * reg returns the dispatcher itself, so it is safe to use as last
 * statement in a with-block.
 *
<pre><code><blockquote>
Dispatcher dispatcher = new Dispatcher().with {
    reg ModelClassA, generatorInstance1
    reg ModelClassB, generatorInstance2
}
</blockquote></code></pre>
 *
 */
interface IDispatcher {

    /**
     * Dispatches a model property.
     *
     * @param model The model to be dispatched.
     */
    public void dispatch(ModelEntity model);

    /**
     * Dispatches the provided models children.
     *
     * @param model The model who's children should be dispatched.
     */
    public void dispatch(ModelProperty model);

    /**
     * Get the generator registered for the provided model(class).
     *
     * @param model The model for which to get the associated generator
     * @return the associated generator
     */
    public IGenerator getGenerator(IModel model);

    /**
     * Registered the Generator to be applied on the provided class when
     * dispatching a model tree.
     *
     * @param cls
     * @param generator
     */
    public void registerGenerator(Class cls, IGenerator generator);

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
    public IDispatcher reg(Class cls, IGenerator generator);
}
