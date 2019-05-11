package com.zenterio.jenkins.models

import groovy.util.GroovyTestCase

class BaseModelTestOperatorOverloading extends GroovyTestCase {

    BaseModel a
    BaseModel b
    BaseModel c

    @Override
    void setUp() throws Exception {
        a = new BaseModel()
        b = new BaseModel()
        c = new BaseModel()
    }

    void testLeftShiftOperatorReturnsSecondOperand() {
        assert b == (a << b)
    }

    void testLeftShiftOperatorCanBeUsedToAddChild() {
        a << b
        assert a.children[0] == b
    }

    void testLeftShiftOperatorCanBeUsedToAddChildren() {
        assert c == a << b << c
        assert a.children[0] == b
        assert b.children[0] == c
    }

    void testLeftShiftOperatorInWithBlock() {
        a.with {
            it << b
            it << c
        }
        assert a.children[0] == b
        assert a.children[1] == c
    }

    void testLeftShiftOperatorWithLineBreaks() {
        a <<
            b <<
                c;
        assert a.children[0] == b
        assert b.children[0] == c
    }

}

