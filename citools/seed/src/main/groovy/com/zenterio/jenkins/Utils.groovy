package com.zenterio.jenkins;

public class Utils {

    public static String safeVariableName(String input) {
        return input?.replaceAll("-", "_")?.replaceAll(/\W/, "")
    }

    public static String safeVariableNameUpperCase(String input) {
        return safeVariableName(input).toUpperCase()
    }

    public static String safeVariableNameLowerCase(String input) {
        return safeVariableName(input).toLowerCase()
    }
}
