package com.zenterio.jenkins.application

import com.zenterio.jenkins.configuration.NoTriggerSeedConfigResolver
import groovy.util.logging.*


/**
 * Seed application that reads XML configuration files and
 * generates jenkins configuration using the Job DSL jenkins plugin.
 *
 * <p>
 * This is a staging version of the ordinary XmlSeedDslApplication, which
 * changes the configuration after reading it, to be suitable for a staging
 * environment
 * <p>
 * See also {@link com.zenterio.jenkins.application.XmlSeedDslApplication}
 */
@Log
class StagingXmlSeedDslApplication extends XmlSeedDslApplication {

    /**
     *
     * @param scriptletsDirectory   Path to scriptlet directory
     * @param jobCreator            Closure factory method for job instantiation.
     * @param buildFlowCreator      Closure factory method for build-flow job instantiation.
     * @param viewCreator           Closure factory method for view instantiation.
     */
    public StagingXmlSeedDslApplication(String scriptletsDirectory,
            Closure jobCreator,
            Closure buildFlowCreator,
            Closure viewCreator)  {
        super(scriptletsDirectory, jobCreator, buildFlowCreator, viewCreator)
        this.resolver = new NoTriggerSeedConfigResolver(this.resolver)
    }
}
