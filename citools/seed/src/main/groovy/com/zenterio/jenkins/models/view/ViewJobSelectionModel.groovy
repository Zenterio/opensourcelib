package com.zenterio.jenkins.models.view

import com.zenterio.jenkins.models.ModelProperty

import java.util.List


class ViewJobSelectionModel extends ModelProperty {

    String jobRegEx
    List<String> jobNames

    public ViewJobSelectionModel(String jobRegEx, List<String> jobNames) {
        super()
        this.jobRegEx = jobRegEx
        this.jobNames = jobNames
    }
}
