package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class ConsoleLogToWorkspaceModel extends ModelProperty {

    String fileName

    ConsoleLogToWorkspaceModel(String fileName)
    {
        this.fileName = fileName
    }
}
