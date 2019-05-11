package com.zenterio.jenkins.logging

import groovy.util.logging.*
import java.util.logging.*

/**
 * The LogConfigurationLoader automatically, on instantiation,
 * looks for the system environment variable
 * COM_ZENTERIO_JENKINS_LOGGING_PROFILE
 * and loads the log profile from the matching properties
 * file located in the logging package.
 * com.zenterio.jenkins.logging/log.{profile}.property
 *
 * If no valid profile was given it retorts to using
 * the "default" profile.
 *
 */
@Log
class LogConfigurationLoader {

    public LogConfigurationLoader() {
        String profile = System.getenv("COM_ZENTERIO_JENKINS_LOGGING_PROFILE")
        switch (profile) {
            case "info":
            case "config":
            case "debug":
            case "all":
            case "quiet":
            case "default":
                //do nothing
                break;
            default:
                log.warning("No valid log profile set (${profile}). Using default.")
                profile="default"
                break;
        }
        InputStream is = null
        try {
            is = this.class.getResourceAsStream("log.${profile}.properties")
            LogManager.getLogManager().readConfiguration(is);
        } finally {
            if (is != null) {
                is.close()
            }
        }
    }
}
