package com.zenterio.jenkins.scriptlet

class FileScriptlet extends BaseScriptlet {

    private String filePath
    private File file

    public FileScriptlet(String filePath) {
        this.filePath = filePath
        this.file = null
    }

    public FileScriptlet(String dirPath, String fileName) {
        this("${dirPath}/${fileName}")
    }

    public String getRawContent() {
        if (this.file == null) {
            this.file = new File(filePath)
        }
        return this.file.text
    }
}
