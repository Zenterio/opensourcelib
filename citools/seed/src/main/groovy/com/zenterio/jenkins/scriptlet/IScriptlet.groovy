package com.zenterio.jenkins.scriptlet

/**
 * Main interface for scriptlets.
 * <p>
 * See {@link com.zenterio.jenkins.scriptlet} for more details of the
 * scriptlet concept.
 */
public interface IScriptlet {

    /**
     * Returns context modified content as string.
     * @return modified content as string.
     */
    public String getContent();

    /**
     * Returns unmodified/raw content as string.
     * @return unmodified/raw content as string.
     */
    public String getRawContent();
}
