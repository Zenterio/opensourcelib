package com.zenterio.jenkins


class UtilsTest extends GroovyTestCase {

    void testSafeVariableNameUnderscoreIsKept() {
        assert Utils.safeVariableName("a_b") == "a_b"
        assert Utils.safeVariableName("a___b_") == "a___b_"
    }

    void testSafeVariableNameDashIsCovertedToUnderscore() {
        assert Utils.safeVariableName("a-b") == "a_b"
        assert Utils.safeVariableName("a---b-") == "a___b_"
    }

    void testSafeVariableNameAlphaNumericIsKept() {
        assert Utils.safeVariableName("abcdefghijklmnopqrstuvxyz") == "abcdefghijklmnopqrstuvxyz"
        assert Utils.safeVariableName("ABCDEFGHIJKLMNOPQRSTUVXYZ") == "ABCDEFGHIJKLMNOPQRSTUVXYZ"
        assert Utils.safeVariableName("0123456789") == "0123456789"
    }

    void testSafeVariableNameOtherCharactersRemoved() {
        assert Utils.safeVariableName("åÄ?!*|\u1234") == ""
    }

    void testSafeVariableNameCombinations() {
        assert Utils.safeVariableName("åaBÄ_-^*2") == "aB__2"
        assert Utils.safeVariableName("-\u2345_") == "__"
    }
}
