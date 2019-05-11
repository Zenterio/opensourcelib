package com.zenterio.jenkins.generators.dsl.view

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.view.ViewJobSelectionModel
import javaposse.jobdsl.dsl.views.ListView.StatusFilter


class ViewJobSelectionGenerator implements IPropertyGenerator {

    private StatusFilter statusFilter

    public ViewJobSelectionGenerator(StatusFilter statusFilter= StatusFilter.ENABLED) {
        this.statusFilter = statusFilter
    }

    @Override
    public void generate(ModelProperty model, Object entity) {
        ViewJobSelectionModel m = (ViewJobSelectionModel)model
        entity.with {
            statusFilter(this.statusFilter)
            jobs {
                if (m.jobNames) {
                    names(*m.jobNames)
                }
                regex(m.jobRegEx)
            }
        }
    }
}
