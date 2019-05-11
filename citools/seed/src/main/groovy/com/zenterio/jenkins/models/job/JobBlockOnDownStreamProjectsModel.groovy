package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

/**
 * Block new builds if a downstream project is currently building
 *
 */
class JobBlockOnDownStreamProjectsModel extends ModelProperty {

    final private Boolean block

    JobBlockOnDownStreamProjectsModel(Boolean block) {
        super()
        this.block = block
    }

    Boolean getBlock() {
        return this.block
    }
}
