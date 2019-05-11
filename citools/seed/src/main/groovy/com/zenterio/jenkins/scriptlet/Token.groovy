package com.zenterio.jenkins.scriptlet

import java.util.regex.Matcher

class Token {

    /**
     * Wraps the key in magic markers and returns a bash/shell token definition.
     * @param key
     * @return token based on key
     */
    public static String token(String key) {
        if (key) {
            return '\\$\\{' + key + '\\}'
        } else {
            return ''
        }
    }

    /**
     * Wraps the key in magic markers and return a groovy token definition
     * @param key
     * @return token based on key
     */
    public static String groovyToken(String key) {
        return "#${key}#"
    }

    /**
     * Returns escaped macro value string.
     *
     * The macro engine in scriptlet uses regex and text containing magic markers
     * need to be escaped if used as the value of a macro expansion, unless the
     * regex group functions is intended to be used.
     *
     * @param txt   Text to be escaped
     * @return  escaped text
     */
    public static String escape(String txt) {
        if (txt) {
            return Matcher.quoteReplacement(txt)
        }
        else {
            return ''
        }
    }

    /**
     * Returns a hash map with keys as the shell and groovy token version of the key parameter,
     * and values as en escaped version of the value parameter
     */
    public static HashMap<String, String> tokenizeAndEscape(String key, String value) {
        return [
                (token(key)) : escape(value),
                (groovyToken(key)) : escape(value)
        ]
    }
}
