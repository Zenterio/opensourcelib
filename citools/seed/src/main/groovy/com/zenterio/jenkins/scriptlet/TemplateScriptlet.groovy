package com.zenterio.jenkins.scriptlet;

public class TemplateScriptlet extends BaseScriptlet {

    private IScriptlet template

    public TemplateScriptlet(IScriptlet template) {
        this.template = template
    }

    @Override
    public String getRawContent() {
        return this.template.getRawContent()
    }

}
