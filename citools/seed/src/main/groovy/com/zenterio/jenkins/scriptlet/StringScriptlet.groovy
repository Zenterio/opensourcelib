package com.zenterio.jenkins.scriptlet

class StringScriptlet extends BaseScriptlet {

    private String content

    public StringScriptlet(String content) {
        this.content = content
    }

    public String getRawContent() {
        return this.content
    }

    public String setRawContent(String rawContent) {
        this.content = rawContent
    }
}
