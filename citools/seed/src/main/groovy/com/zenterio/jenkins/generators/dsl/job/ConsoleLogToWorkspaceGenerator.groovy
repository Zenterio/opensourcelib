package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.ConsoleLogToWorkspaceModel


class ConsoleLogToWorkspaceGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        ConsoleLogToWorkspaceModel m = (ConsoleLogToWorkspaceModel) model
        entity.configure { node ->
            node / 'publishers' / 'hudson.plugins.ConsoleLogToWorkspace.ConsoleLogToWorkspacePublisher' {
                fileName(m.fileName)
                writeConsoleLog(true)
                blockOnAllOutput(true)
            }
        }
    }
}
