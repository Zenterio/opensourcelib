/**
 * The logging package provides a mechanism to configure the java logger
 * to enable specific log levels for com.zenterio.jenkins
 * using different logging profiles that can be set at execution time.
 * <p>
 * The logging framework utilized in the Seed project make use of the following
 * profiles  (mapped to log level):
 * <ul>
 * <li>all (FINEST+method trace)</li>
 * <li>debug (FINER)</li>
 * <li>config (CONFIG)</li>
 * <li>info (INFO)</li>
 * <li>quiet (SEVERE)</li>
 * </ul>
 * The configuration for each profile is stored in a log properties file:
 * <pre>com.zenterio.jenkins.logging/log.{profile}.properties</pre>
 * <p>
 * To turn on logging in your code use the following structure:
 * <pre><code>
 * import groovy.util.logging.*
 *
 * &#064;Log
 * class YourClass {
 *     log.finer("message")   // debug
 *     log.config("message")  // framework configuration
 *     log.info("message")    // info
 *     log.warning("message") // something is not as it should
 *     log.severe("message")  // really bad error
 * }
 * </code></pre>
 * <p>
 * Follow the general guide-lines for use of the different levels.
 * One source of information:
 * <a href='http://www.javapractices.com/topic/TopicAction.do?Id=143'>Logging messages</a>.
 * <p>
 * See {@link com.zenterio.jenkins.logging.LogConfigurationLoader} on how
 * the configuration is loaded.
 */
package com.zenterio.jenkins.logging
