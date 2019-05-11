/**
 *
 * The models package provides a framework for creating and manipulating
 * models that represent tree structures with entities and their properties.
 * <p>
 * The {@link com.zenterio.jenkins.models.IModel} interface specify the framework
 * interaction points from a pure model concept perspective.
 * <p>
 * The {@link com.zenterio.jenkins.models.BaseModel} provides an implementation of
 * IModel but should not be used directly.
 * <p>
 * The {@link com.zenterio.jenkins.models.ModelEntity} class should be inherited
 * from to create nodes in the model tree that represents an entity of some sort.
 * <p>
 * The {@link com.zenterio.jenkins.models.ModelProperty} class should be
 * inherited from to crate nodes in the model tree that represents
 * properties/attributes of the entities.
 * <p>
 * When applying PropertyGenerators
 * ({@link com.zenterio.jenkins.generators.IPropertyGenerator})
 * on a model property, it operates on the associated model entities.
 * <p>
 * Model trees are built be adding child-nodes to parent-nodes.
 * There are several ways to do this:
 * <p>
 * Traditional Java syntax:
 * {@link com.zenterio.jenkins.models.BaseModel#add(com.zenterio.jenkins.models.IModel)}
 * is similar method to
 * {@link com.zenterio.jenkins.models.BaseModel#addChild(com.zenterio.jenkins.models.IModel)}
 * with the difference that it returns the parent node instead
 * of the child node.
<pre><code><blockquote>
IModel parent = new MyParentModel()
parent.addChild(new MyModel())
parent.add(new MyModel())
</blockquote></code></pre>
 * <p>
 * More Groovy style syntax:
<pre><code><blockquote>
IModel parent = new MyParentModel()
parent << new MyModel()
</blockquote></code></pre>
 * <p>
 * The different add-child functions has slightly different behavior to cater
 * to different use scenarios.
 * <p>
 * Left-shift (<<) and addChild() returns the child being added to make it easy
 * to build chains of models:
 * <p>
 * a -> b -> c
 * <p>
 * The following example lines are equivalent:
<pre><code><blockquote>
a.addChild(b).addChild(c)
a << b << c
</blockquote></code></pre>
 * <p>
 * The add() function returns the parent being added to rather than the child
 * being added. This is to make it suitable in with-block use. By return the
 * parent node, the with-block doesn't need to end with returning the implicit
 * this/it reference which is easy to miss and very important when building
 * complex nested structures, see further down.
 * However, this distinction makes it tricky to mix add and << in the same
 * statement. In the same statement, only use one or the other - don't mix!
<pre><code><blockquote>
a.with {
    add b1
    add b2
}
</blockquote></code></pre>
 * <p>
 * To build complex hierarchies, the following coding standard is encouraged:
 * <p>
 * Simple chaining:
<pre><code><blockquote>
a << b << c
</blockquote></code></pre>
 * <p>
 * Multiple branches/children, where some logic is required in between:
<pre><code><blockquote>
a << b1
...
a << b2
...
a << b3
</blockquote></code></pre>
 * <p>
 * Alternatively, if it adds clarity:
<pre><code><blockquote>
a.with {
    add b1
    add b2
    add b3
}
</blockquote></code></pre>
 * <p>
 * For very complex structures, it is best to do the modeling in distinct
 * groups when possible. It is also encouraged that if you have very complex
 * model creation that you first define the models and then bind/define their
 * relationships.
 * <p>
 * Please note the use of streaming to <i>it</i> inside the with-block.
 * This because streaming to an add-ed item will have unexpected behavior due
 * to that add returns the parent, not the child. Hence don't mix add and <<
 * in the same statement. Further, since << returns the child, it should not
 * be used as the last statement in a with-block, since the <i>it</i> of the
 * with-block should be returned, especially in context of initialization.
<pre><code><blockquote>
IModel a = new A()
IModel b1 = new B()
IModel b2 = new B()
IModel c11 = new C()
IModel c12 = new C()
IModel c21 = new C()
IModel d211 = new D()

a.with {
    add b1.with {
        add c1
        add c2
    }
    it << b2 << c21 << d211
}
</blockquote></code></pre>
 * See also associated unit tests for more examples.
 * <p>
 * <strong>How to think about models</strong>
 * <p>
 * A model can have one of the following characteristics:
 * <ul>
 * <li>static</li>
 * <li>dynamic</li>
 * </ul>
 * <p>
 * Static Models
 * <p>
 * A static model hold all of its data as local fields and are not affected
 * by its context.
 * <p>
 * Dynamic Models
 * <p>
 * A dynamic model are context dependent and will search the model tree for
 * data from its surrounding models. A dynamic property, associated with an
 * entity model, will most often apply the context of that entity to determine
 * its own behavior.
 * <p>
 * This require the dynamic model to know what entity model it should probe.
 * A model property should not assume that its parent is the entity, it could
 * be attached to another property and must hence search for its entity parent.
<pre><code><blockquote>
IModel entity = this.getParent(ModelEntity, false)
</blockquote></code></pre>
 * <p>
 * <strong>Searching a Model Tree</strong>
 * <p>
 * The key methods for searching a model tree are:
 * <ul>
 * <li>getChildren(args...) - get matching children as a list</li>
 * <li>getChild(args...) - get first matching child </li>
 * <li>getParent(args...) - get first matching parent</li>
 * <li>getParents(args...) - get a list of all matching parents</li>
 * <li>getProperties(args...) - get a list of matching property models</li>
 * <li>getProperty(args...) - get first matching property model</li>
 * </ul>
 * The following can be used as search criteria:
 * <ul>
 * <li>Class</li>
 * <li>strict match on class</li>
 * <li>recursive</li>
 * <li>pass-filtering closure</li>
 * </ul>
 * Class
 * <p>
 * The model structure should be organized so different representations
 * have different classes. Take care to construct your class hierarchy since
 * the key filter mechanism for searching the tree is based on class.
 * <p>
 * <strong><i>Strict vs Non-strict</i></strong>
 * <p>
 * In strict mode exact class match is required. In Non-strict mode (strict=false)
 * you also get a match if the instance is a sub-class of the sought class.
 * <p>
 * <i>Recursive</i>
 * <p>
 * In non-recursive mode (recursive=false), only the direct children are searched.
 * In recursive mode the entire tree with the starting node as root will be searched.
 * <p>
 * <i>Pass-filtering Closure</i>
 * <p>
 * A closure can be passed. Each node will be passed to the closure together with
 * a list of all results collected so far, and it will be
 * considered a pass of the filter return true. If the filter returns falls, the
 * node will not be included in the search result.
<pre><code><blockquote>
Closure passFilter = { IModel item, ArrayList result ->
  //do something
}
</blockquote></code></pre>
 * <p>
 * The following exceptions can be thrown in the pass-filter to produce the
 * listed results.
 * <ul>
 * <li>{@link com.zenterio.jenkins.models.HaltBranchSearchModelException}
 *     - stops the search in the current branch. Rest of three is still searched.</li>
 * <li>{@link com.zenterio.jenkins.models.HaltTreeSearchModelException}
 *     - stops the search of the entire tree.The results collected so far are
 *     returned.</li>
 * <li>{@link com.zenterio.jenkins.models.InvalidateTreeSearchModelException}
 *     - Invalidates the entire search and an empty result set is returned.</li>
 * </ul>
 * <p>
 * See also {@link com.zenterio.jenkins.models.BaseModel}.
 */
package com.zenterio.jenkins.models
