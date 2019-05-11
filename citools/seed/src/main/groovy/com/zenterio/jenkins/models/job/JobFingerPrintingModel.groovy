package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobFingerPrintingModel extends ModelProperty {

    final String targets

    public JobFingerPrintingModel(String targets) {
        super()
        this.targets = targets
    }

}
