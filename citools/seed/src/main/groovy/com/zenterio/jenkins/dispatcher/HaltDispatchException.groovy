package com.zenterio.jenkins.dispatcher

import com.zenterio.jenkins.models.IModel

class HaltDispatchException extends Exception {

    IModel model

    public HaltDispatchException(IModel model) {
        super("Halt dispatch of model ${model}")
        this.model = model
    }
}
