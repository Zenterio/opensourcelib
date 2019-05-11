package com.zenterio.jenkins.configuration.macroexpansion

import java.beans.Introspector
import java.beans.PropertyDescriptor
import java.beans.BeanInfo

/**
 * The ObjectVisitor traverses object structures, applying the provided transform
 * on all read/write properties of each node.
 *
 * All objects of the type nodeClass or derived thereof, are considered nodes
 * in the structure.
 *
 * Properties from super-classes to nodeClass are not considered.
 *
 * Circular graphs are allowed.
 *
 * Using plain Object as nodeClass is not recommended as the Object class comes
 * with a lot of properties probably not of interest.
 *
 * Arrays, lists and maps can never be considered nodes in the structure, but are treated
 * as references to other nodes. Items in lists, arrays and maps are also passed
 * to the transformer as though have been properties of a node.
 * Arrays, lists and maps are not passed to the transformer either.
 *
 * None-node objects are passed to the transformer, but are not checked for
 * references to other nodes.
 * Node objects themselves are also passed to the transformer.
 *
 * The ObjectVisitor is a generic class, and the generic type MUST match that
 * of the nodeClass. Limitations in the java/groovy language forces the construct
 * of passing it both as a generics parameter and as argument to the constructor.
 * The ITransform should also be of the same generic type as the ObjectVisitor.
 */
class ObjectVisitor<T> {

    protected static Map<Class, BeanInfo> beanCache = new HashMap<Class, BeanInfo>()
    protected final ITransform transform
    protected final Class nodeClass
    protected final Class stopClass

    /**
     * @param transform
     * @param nodeClass
     */
    public ObjectVisitor(ITransform<T> transform, Class nodeClass) {
        this.transform = transform
        this.nodeClass = nodeClass
        this.stopClass = this.nodeClass.getSuperclass() ?: Object.class
    }

    /**
     * @param obj
     * @param context
     */
    public Object visit(Object obj, List<T> context = new ArrayList<T>()) {
        if (obj == null) {
            return obj
        }
        obj = this.transform.transform(obj, context)
        if (this.isOfBaseClass(obj)) {
            this.visitNode(obj, context)
        }
        return obj
    }

    /**
     * @param arr
     * @param context
     */
    public Object[] visit(Object[] arr, List<T> context = new ArrayList<T>()) {
        arr.eachWithIndex { it, index ->
            if (it != null) {
                arr[index] = this.visit(it, context)
            }
        }
        return arr
    }

    /**
     * @param list
     * @param context
     */
    public List visit(List list, List<T> context = new ArrayList<T>()) {
        list.eachWithIndex { it, index ->
            if (it != null) {
                list[index] = this.visit(it, context)
            }
        }
        return list
    }

    /**
     * @param map
     * @param context
     */
    public Map visit(Map map, List<T> context = new ArrayList<T>()) {
        map.each { key, value ->
            if (value != null) {
                map[key] = this.visit(value, context)
            }
        }
        return map
    }

    /**
     * @param node
     * @param context
     */
    protected void visitNode(T node, List<T> context) {
        if (this.hasBeenVisited(node, context)) {
            return
        }

        BeanInfo info = getBeanInfo(node)
        PropertyDescriptor[] props = info.getPropertyDescriptors()
        List<T> updatedContext = this.getUpdatedContext(context, node)
        props.each { PropertyDescriptor pd ->
            Object value = this.readValue(node, pd)
            if (value != null) {
                if (this.isNoneWritable(value) || this.isNoneWritableProperty(pd)) {
                    this.visit(value, updatedContext)
                } else {
                    this.writeValue(node, pd,
                        this.visit(value, updatedContext))
                }
            }
        }
    }

    /**
     * The traditional java for loop is at least x2-4 as fast
     * as groovy .find {}
     */
    protected boolean hasBeenVisited(T node, List<T> context) {
        for(T n: context) {
            if (n.is(node)) {
                return true
            }
        }
        return false
    }

    /**
     * @param context
     * @param node
     */
    protected List<T> getUpdatedContext(List<T> context, T node) {
        return (context + [node]) as List<T>
    }

    /**
     * @param node
     * @param pd
     */
    protected Object readValue(T node, PropertyDescriptor pd) {
        return pd.getReadMethod().invoke(node)
    }

    /**
     * @param node
     * @param pd
     * @param value
     */
    protected void writeValue(T node, PropertyDescriptor pd, Object value) {
        if (node != null && value != null && (!this.isZeroSizedArrayLike(value))) {
            pd.getWriteMethod().invoke(node, value.asType(pd.getPropertyType()))
        }
    }

    /**
     * @param obj
     */
    protected boolean isOfBaseClass(Object obj) {
        if (obj == null) {
            return false
        }
        return obj.class in this.nodeClass
    }

    /**
     * @param obj
     */
    protected boolean isZeroSizedArrayLike(Object obj) {
        return (this.isArray(obj) || this.isCollection(obj)) && obj.size == 0
    }

    /**
     * @param pd
     */
    protected boolean isNoneWritableProperty(PropertyDescriptor pd) {
        return pd.getWriteMethod() == null
    }

    /**
     * @param obj
     */
    protected boolean isNoneWritable(Object obj) {
        return isArray(obj) || isCollection(obj) || isMap(obj)
    }

    /**
     * @param obj
     */
    protected boolean isCollection(Object obj) {
        return Collection.class.isAssignableFrom(obj.getClass())
    }

    /**
     * @param obj
     */
    protected boolean isArray(Object obj) {
        return obj.getClass().isArray()
    }

    /**
     * @param obj
     */
    protected boolean isMap(Object obj) {
        return Map.class.isAssignableFrom(obj.getClass())
    }

    protected BeanInfo getBeanInfo(T node) {
        BeanInfo info = beanCache.get(node.class)
        if (info == null) {
            info = Introspector.getBeanInfo(node.class, this.stopClass, Introspector.IGNORE_ALL_BEANINFO)
            beanCache.put(node.class, info)
        }
        return info
    }

}
