package com.zenterio.jenkins.generators.dsl

class NodeUtils {
    static public String getNodeContent(Node node, String... path) {
        Node n = node
        try {
            return getNode(node, path).text()
        } catch (NullPointerException e) {
            return ""
        }
    }

    static public void setNodeContent(Node node, Object value, String... path) {
        try {
            getNode(node, path).value = value
        } catch (NullPointerException e) {
            // do nothing
        }
    }

    static public Node getNode(Node node, String... path) {
        Node n = node
        try {
            for (String p : path) {
                n = n.get(p)[0]
            }
            return n
        } catch (NullPointerException e) {
            return null
        }
    }
}
