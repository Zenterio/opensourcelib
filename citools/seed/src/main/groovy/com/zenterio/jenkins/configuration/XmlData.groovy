package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.AutoCloneStyle
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone(style=AutoCloneStyle.COPY_CONSTRUCTOR)
class XmlData extends BaseConfig {

    /**
     * Source class in the XML file to read from
     */
    final String source

    /**
     * The operation to perform
     */
    final XmlDataOperation operation

    /**
     * Field in the XML file to read from
     */
    final String field

    /**
     * Caption/header for the data
     */
    final String caption

    XmlData(String source, XmlDataOperation operation, String field, String caption) {
        this.source = source ?: ""
        this.operation = operation
        this.field = field ?: ""
        this.caption = caption ?: ""
    }

    public static XmlData getTestData() {
        XmlData data = new XmlData("source.in.xml", XmlDataOperation.AVG, "Field", "Caption")
        return data
    }

}
