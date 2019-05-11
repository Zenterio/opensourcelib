package com.zenterio.jenkins.generators.dsl

import groovy.util.GroovyTestCase

class NodeUtilsTest extends GroovyTestCase {

   public void test_getNodeContentReturnValueOfValidNodePath() {
       Node n = new Node(null, "root")
       n.appendNode("a").appendNode("b").appendNode("c", "TEXT")
       assert "TEXT" == NodeUtils.getNodeContent(n, 'a', 'b', 'c')
   }

   public void test_getNodeContentReturnEmptyStringForInvalidNodePath() {
       assert "" == NodeUtils.getNodeContent(new Node(null, "root"), 'does-not-exist')
   }

   public void test_setNodeContentUpdatesValueForValidNodePath() {
       Node n = new Node(null, "root")
       n.appendNode("a").appendNode("b").appendNode("c")
       NodeUtils.setNodeContent(n, "TEXT", 'a', 'b', 'c')
       assert "TEXT" == NodeUtils.getNodeContent(n, 'a', 'b', 'c')
   }

   public void test_setNodeFailsSilentlyForInvalidNodePath() {
       NodeUtils.setNodeContent(new Node(null, "root"), "TEXT", 'does-not-exist')
   }

}

