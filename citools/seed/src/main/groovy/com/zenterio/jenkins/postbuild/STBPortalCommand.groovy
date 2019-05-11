package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.scriptlet.FileScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import static com.zenterio.jenkins.scriptlet.Token.token
import static com.zenterio.jenkins.scriptlet.Token.escape

class STBPortalCommand extends TemplateScriptlet{

    public STBPortalCommand(String scriptletsDirectory, String command, String commandInit='',
                            String commandCondition='true') {
        super(new FileScriptlet("${scriptletsDirectory}/STBPortalCommand.groovy"))
        this.addMacroDefinitions([
                (token('STB_PORTAL_COMMAND')): escape(command),
                (token('STB_PORTAL_COMMAND_INIT')): escape(commandInit),
                (token('STB_PORTAL_COMMAND_CONDITION')): escape(commandCondition),
        ])
    }
}
