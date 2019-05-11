package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.FileScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token

class StoreAuthorsScriptlet extends BuildStepScriptlet{
    StoreAuthorsScriptlet(String scriptletDirectory,
                          String productName,
                          int swUpgradeOffset,
                          Repository[] repositories) {
        super(new FileScriptlet(scriptletDirectory,"store-authors"), productName, swUpgradeOffset)

        this.addMacroDefinitions([(token('REPO_PATH_LIST')):
                                          escape(getQuotedBashStringList(repositories.collect({Repository it -> "\$WORKSPACE/${it.directory}"})))])

        this.addMacroDefinitions([(token('REPO_NAME_LIST')):
                                          escape(getQuotedBashStringList(repositories.collect({Repository it -> it.name})))])
    }

    private getQuotedBashStringList(Collection collection) {
        return collection.collect({it -> "\"${it}\""}).join(' ')
    }
}
