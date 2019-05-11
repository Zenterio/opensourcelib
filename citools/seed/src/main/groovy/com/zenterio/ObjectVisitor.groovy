package com.zenterio

import java.beans.Introspector
import java.beans.PropertyDescriptor
import java.beans.BeanInfo

import static com.zenterio.TypeUtils.isMap
import static com.zenterio.TypeUtils.isCollection
import static com.zenterio.TypeUtils.isArray
import static com.zenterio.TypeUtils.isZeroSizedArrayLike

/**
 * The ObjectVisitor traverses object structures, applying the provided action
 * on all read properties of each node.
 *
 * All objects of the type nodeClass or derived thereof, are considered nodes
 * in the structure.
 *
 * Properties from super-classes to nodeClass are not considered.
 *
 * Circular graphs are allowed. The second time an object is found, it is still
 * passed to the action, but its properties are not traversed a second time.
 * Hence, if an object is guaranteed to only be processed once, the IActionVisit
 * instance must itself keep track of visited objects.
 *
 * Using plain Object as nodeClass is not recommended as the Object class comes
 * with a lot of properties probably not of interest.
 *
 * Arrays, lists and maps are considered nodes in the structure even if not of node type.
 * Items in lists, arrays and maps are also passed
 * to the action as though have been properties of a node.
 *
 * None-node objects are passed to the action, but are not checked for
 * references to other nodes and their properties are not traversed.
 *
 * The ObjectVisitor is a generic class, and the generic type MUST match that
 * of the nodeClass. Limitations in the java/groovy language forces the construct
 * of passing it both as a generics parameter and as argument to the constructor.
 * The IActionVisit should also be of the same generic type as the ObjectVisitor.
 */
class ObjectVisitor<T> {

    protected final IActionVisit<T> action
    protected final Class nodeClass
    protected final Class stopClass
    protected final List<T> visitedNodes

    /**
     * @param action
     * @param nodeClass
     */
    public ObjectVisitor(IActionVisit<T> action, Class nodeClass) {
        this.action = action
        this.nodeClass = nodeClass
        this.stopClass = this.nodeClass.getSuperclass() ?: Object.class
        this.visitedNodes = new ArrayList<T>()
    }

    /**
     * @param obj
     * @param context
     */
    public void visit(Object obj, List<T> context = new ArrayList<Object>(), String propertyName = null) {
        if (this.isNode(obj)) {
            this.visitNode(obj, context, propertyName)
        } else {
            this.action.perform(obj, context, propertyName)
        }
    }

    /**
     * @param arr
     * @param context
     */
    public void visit(Object[] arr, List<T> context = new ArrayList<Object>(), String propertyName = null) {
        this.action.perform(arr, context, propertyName)
        List<T> updatedContext = this.getUpdatedContext(context, arr)
        arr.eachWithIndex { it, index ->
            this.visit(it, updatedContext, "[${index.toString()}]")
        }
    }

    /**
     * @param list
     * @param context
     */
    public void visit(List list, List<T> context = new ArrayList<Object>(), String propertyName = null) {
        this.action.perform(list, context, propertyName)
        List<T> updatedContext = this.getUpdatedContext(context, list)
        list.eachWithIndex { it, index ->
            this.visit(it, updatedContext, "[${index.toString()}]")
        }
    }

    /**
     * @param map
     * @param context
     */
    public void visit(Map map, List<T> context = new ArrayList<Object>(), String propertyName = null) {
        this.action.perform(map, context, propertyName)
        List<T> updatedContext = this.getUpdatedContext(context, map)
        map.each { key, value ->
            this.visit(value, updatedContext, "[${key.toString()}]")
        }
    }

    /**
     * @param node
     * @param context
     */
    protected void visitNode(T node, List<T> context, String propertyName) {
        if (this.hasBeenVisited(node, context)) {
            return
        } else {
            this.visitedNodes.add(node)
        }
        this.action.perform(node, context, propertyName)

        BeanInfo info = Introspector.getBeanInfo(node.class, this.stopClass, Introspector.IGNORE_ALL_BEANINFO)
        PropertyDescriptor[] props = info.getPropertyDescriptors()
        List<T> updatedContext = this.getUpdatedContext(context, node)
        props.each { PropertyDescriptor pd ->
            Object value = this.readValue(node, pd)
            if (value instanceof MetaClass) {
                return
            }
            if (value == null) {
                this.visit((Object)value, updatedContext, pd.getName())
            } else {
                this.visit(value, updatedContext, pd.getName())
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
     * @param obj
     */
    public boolean isNode(Object obj) {
        if (obj == null) {
            return false
        }
        return obj.class in this.nodeClass
    }

}
