package com.zenterio.jenkins.models.display

import com.zenterio.jenkins.models.job.JobDescriptionModel


class DescriptionDisplayModel extends JobDescriptionModel {

    public DescriptionDisplayModel(String description) {
        super(description)
    }

    @Override
    public String getDescription(){
        String result = ""
        if (this.@description) {
            result =  """\
<div style='display: inline-block; min-width: 400px; max-width: 40%; vertical-align: top; margin: 10px; border: 1px solid #bbbbbb; padding: 5px 10px; background: #f0f0f0; border-radius:10px; box-shadow: 5px 5px 5px #888888;'>
    <p style='background: inherit'>${this.@description}</p>
</div>
"""
        }
        return result
    }
}
