package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.PublishOverSSHList
import com.zenterio.jenkins.models.ModelProperty


class JobPublishOverSSHListModel extends ModelProperty {

    PublishOverSSHList publishOverSSHList

    public JobPublishOverSSHListModel(PublishOverSSHList publishOverSSHList) {
        this.publishOverSSHList = publishOverSSHList
    }
}
