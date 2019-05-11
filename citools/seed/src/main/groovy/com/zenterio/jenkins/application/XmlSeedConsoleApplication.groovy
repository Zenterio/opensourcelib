package com.zenterio.jenkins.application

import com.zenterio.jenkins.dispatcher.LooseMatchDispatcher
import com.zenterio.jenkins.models.BaseModel;
import com.zenterio.jenkins.generators.console.SimpleTextGenerator

import groovy.util.logging.*


/**
 * Seed application that reads XML configuration files and generates
 * a description of the built model, written to stdout.
 * <p>
 * The application is also dependent on path to where the scriptlet files
 * are located. See also {@link com.zenterio.jenkins.scriptlet}.
 * <p>
 * This class is a specialization of the XmlSeedBaseApplication using an
 * ExactMatchDispatcher.
 */
@Log
class XmlSeedConsoleApplication extends XmlSeedBaseApplication {

    public XmlSeedConsoleApplication(String scriptletsDirectory) {
        super (new LooseMatchDispatcher(true), scriptletsDirectory)
        this.configureDispatcher()
    }

    private void configureDispatcher() {
        this.dispatcher.with {
            reg BaseModel, new SimpleTextGenerator(System.out)
        }
    }
}
