package com.zenterio.jenkins.scriptlet

import groovy.util.logging.*

/**
 * This class implements the macro expansion engine that should be used
 * to define macros in more specialized classes. The code example below
 * illustrates the use of a parameterized scriptlet to let custom values
 * be used for the expansion of a given macro-token.
 * <p>
 * Code example:
<pre><code><blockquote>
MyScriptlet extends BaseScriptlet {
    public MyScriptlet(String someParam) {
        super()
        this.addMacroDefinitions(["MY_MACRO": "Expanded value",
                                  "TOKEN": someParam])
    }
}
</blockquote></code></pre>
 * <p>
 * Macros are defined by passing a hash-map/dictionary to the
 * addMacroDefinitions() method. Where keys are the macro-tokens that should be
 * expanded, and value part of the hash-map entry is the expanded value.
 * <p>
 * The macro-expansion engine is multi-pass meaning that, if the expanded
 * value of a macro-token contain the token for another macro, that too will
 * be expanded. A runtime error will be thrown if the expansion enters an
 * infinite loop.
 * <p>
 * Example:
<pre><code><blockquote>
["#MSG#": "Hello #NAME#!",
 "#NAME#: "Gandalf"]
</blockquote></code></pre>
 * <p>
 * The above example will expand &#35;MSG&#35; to "Hello Gandalf!".
 * <p>
 * The example below will throw a runtime exception when expanding "GNU" due to
 * infinite loop.
 * <p>
<pre><code><blockquote>
["GNU": "GNU's Not Unix!"]
</blockquote></code></pre>
 */
@Log
public abstract class BaseScriptlet implements IScriptlet {

    /**
     * Holds the macro definitions, key=TOKEN, value=expanded value.
     */
    private Map<String, String> macros

    public BaseScriptlet() {
        this.macros = new LinkedHashMap<String, String>()
    }

    /**
     * Abstract method that should return the raw unmodified content.
     * This is implementation specific and should be implemented in the sub-class
     * that uses this class as base.
     * This method is also called by getContent() as part of generating the
     * macro-expanded version of the raw content.
     * @return raw content as string
     */
    public abstract String getRawContent()

    /**
     * Returns the macro expanded version of the raw content. If no macros are
     * defined or, the macro-tokens are not present in the raw content, then
     * the getRawContent() and getContent() will return the same thing.
     * @return macro-expanded content.
     */
    public String getContent() {
        String result = this.getRawContent()
        String oldResult = null
        Boolean foundNewResult = true
        int i = 0

        /*
         * Iterate over each macro expansion until no new expansion is done; hence
         * no new results are found when expanding the macros.
         * Iterating at most one pass for each macro, gives each macro chance
         * to have effect at least once after every other macro-expansion.
         * One extra pass since last valid pass over the loop should be
         * done without any changes.
         */
        while (foundNewResult) {
            foundNewResult = false
            this.macros.each { macro ->
                oldResult = result
                log.finest("Scriptlet macro-expansion (key=${macro.key}, value=${macro.value})")
                result = result.replaceAll(macro.key, macro.value)
                if (result != oldResult) {
                    foundNewResult = true
                }
            }

            if (i > this.macros.size()) {
                throw new RuntimeException("Infinite loop due to recursive macro-expansion.")
            }
            i++
        }
        return result
    }

    /**
     * Adds the macro definitions using a map, override existing ones with the same
     * key. Key: MacroName, Value: The value of the macro.
     * @param newMacros Map of new macro definitions.
     */
    protected void addMacroDefinitions(Map<String, String> newMacros) {
        this.macros.putAll(newMacros)
    }

    /**
     * Clears macro definitions.
     */
    protected void clearMacroDefinitions() {
        this.macros.clear()
    }
}
