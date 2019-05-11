package com.zenterio.jenkins.application

import com.zenterio.jenkins.generators.*;
import com.zenterio.jenkins.generators.view.*;
import com.zenterio.jenkins.generators.job.*
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel;
import com.zenterio.jenkins.models.job.*;
import com.zenterio.jenkins.models.view.*;
import com.zenterio.jenkins.builders.JenkinsModelBuilder
import com.zenterio.jenkins.configuration.*;
import com.zenterio.jenkins.dispatcher.IDispatcher
import com.zenterio.jenkins.configuration.xml.*

import groovy.util.logging.*


/**
 * Application that reads XML configuration.
 * <p>
 * It is pre-configured with configuration reader/parser for XML, a standard
 * config resolver and standard Jenkins Model builder.
 * <p>
 * The dispatcher and scriptlet path directory is configurable via the
 * constructor.
 *  <p>
 * This class is a specialization of the SeedApplication class using:
 * <ul>
 *  <li>ConfigXmlReader</li>
 *  <li>SeedConfigMerger</li>
 *  <li>SeedConfigResolver</li>
 *  <li>JenkinsModelBuilder</li>
 * </ul>
 */
@Log
class XmlSeedBaseApplication extends SeedApplication {

    /**
     *
     * @param dispatcher            Dispatcher instance
     * @param scriptletsDirectory   Path to where scriptlets are located.
     */
    public XmlSeedBaseApplication(IDispatcher dispatcher, String scriptletsDirectory) {
        super(dispatcher,
              new ConfigXmlReader(new ConfigXmlParser()),
              new SeedConfigMerger(),
              new SeedConfigResolver(),
              { projects ->
                  new JenkinsModelBuilder(projects, scriptletsDirectory)
              })
    }
}
