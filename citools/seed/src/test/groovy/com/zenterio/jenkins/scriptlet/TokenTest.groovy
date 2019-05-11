package com.zenterio.jenkins.scriptlet

import groovy.util.GroovyTestCase;
import static Token.token
import static Token.escape

class TokenTest  extends GroovyTestCase {


    public void testEmptyKeyGivesEmptyToken() {
        assert token('') == ''
    }

    public void testNonEmptyKeyGivesValidToken() {
        assert token('KEY') == '\\$\\{KEY\\}'
    }

    public void testNullKeyGivesEmptyToken() {
        assert token(null) == ''
    }

    public void testEmptyEscapeGivesEmptyValue() {
        assert escape('') == ''
    }

    public void testNonEmptyEscapeGivesEscapedValue() {
        assert escape('$$') == '\\$\\$'
    }

    public void testNullEscapeGivesEmptyValue() {
        assert escape(null) == ''
    }
}