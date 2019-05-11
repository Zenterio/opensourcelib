package com.zenterio.jenkins.configuration

public enum XmlDataOperation {
    AVG("avg"),
    MIN("min"),
    MAX("max")

    private final String operation

    private XmlDataOperation(String operation) {
        this.operation = operation
    }

    @Override
    public String toString() {
        return this.operation
    }

    public static XmlDataOperation getFromString(String operation) {
        return operation.toUpperCase() as XmlDataOperation
    }
}
