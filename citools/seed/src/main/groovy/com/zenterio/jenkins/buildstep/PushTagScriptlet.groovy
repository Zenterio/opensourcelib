package com.zenterio.jenkins.buildstep;

import com.zenterio.jenkins.configuration.Repository;
import com.zenterio.jenkins.scriptlet.BaseScriptlet;

public class PushTagScriptlet extends BaseScriptlet {


    private Repository[] repositories;

    public PushTagScriptlet(Repository[] repositories) {

        this.repositories = repositories;
    }

    @Override
    public String getRawContent() {
        String content = "#!/usr/bin/env bash\nset -eux\n\n"
        this.repositories.each({ repo ->
            content += "cd \"\${WORKSPACE}/${repo.directory}\"\n"
            content += "git push ${repo.name} \"\${BUILD_TAG}\"\n\n"
        })
        return content
    }

}
