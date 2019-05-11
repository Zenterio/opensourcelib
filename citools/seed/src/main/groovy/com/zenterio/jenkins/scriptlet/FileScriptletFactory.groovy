package com.zenterio.jenkins.scriptlet

/**
 * Helper factory to make it easy to create FileScriptlets from a given
 * directory and not needing to repeatedly provide the same directory.
 */
class FileScriptletFactory {

    final private scriptletDirectory

    public FileScriptletFactory(String scriptletDirectory) {
        this.scriptletDirectory = scriptletDirectory
    }

    public FileScriptlet fromFile(String fileName) {
        return new FileScriptlet(this.scriptletDirectory, fileName)
    }
}
