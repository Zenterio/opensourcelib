package com.zenterio

import java.beans.Introspector
import java.beans.PropertyDescriptor
import java.beans.BeanInfo
import java.io.StringWriter
import java.io.Writer
import groovy.json.JsonOutput

import static com.zenterio.TypeUtils.isMap
import static com.zenterio.TypeUtils.isCollection
import static com.zenterio.TypeUtils.isArray
import static com.zenterio.TypeUtils.isZeroSizedArrayLike
import static com.zenterio.TypeUtils.isArrayLike
import static com.zenterio.SafeHtml.htmlEscape



/**
 * Traverses object structures, converting each field to a jqTree node in
 * JSON format.
 *
 * Circular graphs are allowed but references to already visited nodes are replaced
 * with their class and hash code instead. This is also true if two objects
 * reference the same object.
 *
 * Newline characters are replaced with &lt;br/&gt;.
 *
 * All values are HTML-escaped
 */
class JSTreeJson<T> implements IActionVisit<T> {

    protected ObjectVisitor<T> visitor
    protected Writer content
    protected Integer indexId
    protected boolean firstWrite
    boolean printId
    boolean printClass

    public JSTreeJson(Class nodeClass, boolean printId = true, boolean printClass = true) {
        this.visitor = new ObjectVisitor<T>(this, nodeClass)
        this.printId = printId
        this.printClass = printClass
        this.init()
    }

    /**
     * @param obj
     */
    public String toJson(Object obj) {
        this.init()
        this.writeJson(obj)
        return this.content.toString()
    }

    public void toJsonFile(String path, Object obj) {
        File f = new File(path)
        f.getParentFile().mkdirs()
        f.withWriter('utf-8') { writer ->
            this.init(writer)
            this.writeJson(obj)
        }
    }

    protected void init(Writer writer = new StringWriter()) {
        this.content = writer
        this.indexId = 0
        this.firstWrite = true
    }

    protected writeJson(Object obj) {
        this.content.append("[")
        this.visitor.visit(obj)
        this.content.append("]")
    }

    public void perform(Object obj, List<T> context, String propertyName) {
        this.jsonTreeNode(propertyName, obj, this.getParentId(context))
    }

    public void perform(Object[] arr, List<T> context, String propertyName) {
        this.jsonTreeNode(propertyName, arr, this.getParentId(context))
    }

    protected String getContent() {
        return this.content.toString()
    }

    protected String getId(Object obj) {
        String id = Integer.toHexString(System.identityHashCode(obj))
        if (id == "0") {
            id = "null@" + Integer.toHexString(this.indexId)
            this.indexId += 1
        }
        return id
    }

    protected String getParentId(List<T> context) {
        if (context.size > 0) {
            return this.getId(context.last())
        } else {
            return "#"
        }
    }

    protected String getObjectHeader(Object obj) {
        if (obj == null) {
            return "NULL"
        }
        String header = ""
        if (this.printClass) {
            String className = obj?.getClass()?.getName() ?: ""
            header = className
        }
        if (this.printId) {
            String id = this.getId(obj)
            header += "@" + id
        }
        return header
    }

    protected String jsonTreeNode(String nodeName, Object obj, String parentId="#") {
        String displayValue = this.getDisplayValue(obj)
        boolean isMultiline = displayValue.find("\n")
        boolean hasNodeName = (nodeName != null)
        boolean hasValue = (obj != null)
        String id = null

        if (isMultiline) {
            if (hasNodeName) {
                id = this.getId(null)
                this.newLine()
                this.writeJsonTreeNode(this.getJsonTreeNodeTextHeader(nodeName), id, parentId)
                parentId = id
            }
            id = this.getId(obj)
            this.newLine()
            this.writeJsonTreeNode(this.getJsonTreeNodeTextContent(displayValue), id, parentId)
        } else {
            id = this.getId(obj)
            this.newLine()
            if (hasValue && hasNodeName) {
                displayValue = nodeName + ": " + displayValue
            } else if(hasNodeName) {
                displayValue = nodeName
            }
            this.writeJsonTreeNode(this.getJsonTreeNodeTextHeader(displayValue), id, parentId)
        }
        return id
    }

    protected String getDisplayValue(Object obj) {
        String value
        if (obj instanceof Boolean ||
            obj instanceof Byte ||
            obj instanceof Short ||
            obj instanceof Integer ||
            obj instanceof Long ||
            obj instanceof Float ||
            obj instanceof Double ||
            obj instanceof String) {
            value = obj.toString()
        } else if ((obj == null) || isArrayLike(obj) || this.visitor.isNode(obj)) {
            value =  this.getObjectHeader(obj)
        } else {
            value = obj.toString()
        }
        value = htmlEscape(value, false)
        return value
    }

    /**
     * @param text The text string is assumed to be quoted json escaped
     * @param id Node id
     * @param parentId Parent node id
     */
    protected void writeJsonTreeNode(String text, String id, String parentId) {
        this.content.append("""{"id":"${id}","parent":"${parentId}","text":""")
        this.content.append(text)
        this.content.append(',"state":{"opened":"true"}}')
        //this.content.append('}')
    }

    protected String getJsonTreeNodeTextHeader(String value) {
        return JsonOutput.toJson("<span class='zenterio-header'>${value}</span>")
    }

    protected String getJsonTreeNodeTextContent(String value) {
        return JsonOutput.toJson("<div class='zenterio-content'>${value}</div>")
    }

    protected String newLine() {
        if (!this.firstWrite) {
            this.content.append(",\n")
        } else {
            this.firstWrite = false
        }
    }

}
