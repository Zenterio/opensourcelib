package com.zenterio.jenkins.scriptlet

import static com.zenterio.jenkins.scriptlet.Token.token
import static com.zenterio.jenkins.scriptlet.Token.escape

import groovy.util.GroovyTestCase;


class StringScriptletTest  extends GroovyTestCase {

    private String rawMsg
    private StringScriptlet ss

    public void setUp() {
        this.rawMsg = 'Hello ${WHAT}!'
        this.ss = new StringScriptlet(rawMsg)
        this.ss.addMacroDefinitions([(token('WHAT')): 'World'])
    }

    public void testRawContentReturnsUnexpandedContent() {
        assert this.ss.getRawContent() == this.rawMsg
    }

    public void testGetContentReturnMacroExpandedContent() {
        assert this.ss.getContent() == 'Hello World!'
    }

    public void testClearMacroDefinitionsMakesExpandedContentSameAsRawContent() {
        this.ss.clearMacroDefinitions()
        assert this.ss.getContent() == this.rawMsg
    }

    public void testAddMacroDefinitionsOverRideExistingKey() {
        this.ss.addMacroDefinitions([(token('WHAT')): 'Brave New World'])
        assert this.ss.getContent() == 'Hello Brave New World!'
    }

    public void testMacrosUsesRegExAndDollarSignMustBeEscapedUsingTokenEscape() {
        this.ss.addMacroDefinitions([(token('WHAT')): escape('$$')])
        assert this.ss.getContent() == 'Hello $$!'
    }

    public void testMacrosUsesRegExAndCurliesMustBeEscapedUsingTokenEscape() {
        this.ss.addMacroDefinitions([(token('WHAT')): escape('{}')])
        assert this.ss.getContent() == 'Hello {}!'
    }

    public void testMacrosUsesRegExAndMagicTokensMustBeEscapedUsingTokenEscape() {
        this.ss.addMacroDefinitions([(token('WHAT')): escape('!${}|<>*.')])
        assert this.ss.getContent() == 'Hello !${}|<>*.!'
    }

    public void testMacroExpansionUsesMultiPass() {
        /* Note!,
         * The macros must be defined in reverse order to test multi-pass,
         * since single-pass can expand all macros defined in order.
         */
        this.ss = new StringScriptlet("1")
        this.ss.addMacroDefinitions(["3": "FINAL",
                                     "2": "3",
                                     "1": "2",])
        assert this.ss.getContent() == "FINAL"

    }

    public void testPreserveToken() {
        this.ss.addMacroDefinitions([(token('WHAT')): escape('${WHAT}')])
        assert this.ss.getContent() == 'Hello ${WHAT}!'
    }

    public void testMacroExpansionThrowsExceptionOnInfiniteLoop() {
        this.ss = new StringScriptlet("GNU")
        this.ss.addMacroDefinitions(["GNU": "GNU'S NOT UNIX"])
        shouldFail(RuntimeException) {
            this.ss.getContent()
        }
    }
}
