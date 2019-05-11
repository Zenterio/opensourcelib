package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.JoinModel

class JobBuildFlowJoinModel extends JoinModel {

    public JoinModel join(IModel... models) {
        for (IModel m: models) {
            m << this
        }
        return this
    }
}
