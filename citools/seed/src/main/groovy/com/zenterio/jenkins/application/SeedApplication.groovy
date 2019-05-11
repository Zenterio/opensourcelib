package com.zenterio.jenkins.application

import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.IConfigReader
import com.zenterio.jenkins.configuration.IConfigMerger
import com.zenterio.jenkins.configuration.IConfigResolver
import static com.zenterio.jenkins.configuration.FilterProjects.filterProjects
import com.zenterio.jenkins.dispatcher.IDispatcher
import com.zenterio.jenkins.models.IModel

import groovy.util.logging.*

/**
 * The Seed Application is configurable via its constructor with
 * dispatcher, configuration reader, configuration resolver and build-creator.
 *
 * The Seed directory and seed file are interfaces for a seed template method
 * that seeds using the following steps:
 * <ul>
 *  <li>Read the source configuration from file or directory</li>
 *  <li>Resolve the raw configuration using the resolver</li>
 *  <li>Create a model-builder using the passed in buildCreator factory method
 *      passing the refined configuration as argument to the factory method.</li>
 *  <li>Build the model tree using the model-builder.</li>
 *  <li>Dispatch the model tree using the dispatcher which in turn will call
 *      registered generators based on the model tree.</li>
 * </ul>
 *
 */
@Log
class SeedApplication {

    protected IDispatcher dispatcher
    protected IConfigReader reader
    protected IConfigMerger merger
    protected IConfigResolver resolver
    protected Closure buildCreator

    /**
     *
     * @param dispatcher    Dispatcher instance
     * @param reader        Configuration reader instance
     * @param merger        Configuration merger instance
     * @param resolver      Configuration resolver instance
     * @param buildCreator  A factory method in the form of a closure that
     *                      takes one argument, an array of Project configuration
     *                      objects and returns a IModelBuilder.
     */
    public SeedApplication(IDispatcher dispatcher,
            IConfigReader reader,
            IConfigMerger merger,
            IConfigResolver resolver,
            Closure buildCreator) {
        this.dispatcher = dispatcher
        this.reader = reader
        this.merger = merger
        this.resolver = resolver
        this.buildCreator = buildCreator
    }

    /**
     *
     * @param path  Path to the directory where the configuration source is
     *              located.
     * @param configFileFilter List of config file names that should be processed. All if empty.
     * @param projectFilter List of project names that should be seeded. All if empty.
     */
    public void seedDirectory(String path,
            List<String> configFileFilter = new ArrayList<String>(),
            List<String> projectFilter = new ArrayList<String>()) {
        log.info("Seed directory (path=${path})")
        log.info("Config file filter (filter=${configFileFilter})")
        log.info("Project filter (filter=${projectFilter})")
        Project[] projects = filterProjects(this.reader.readDirectory(path, configFileFilter), projectFilter)
        this.seed(projects)
    }

    /**
     *
     * @param path  Path to the file to use as configuration source.
     * @param projectFilter List of project names that should be seeded. All if empty.
     */
    public void seedFile(String path, List<String> projectFilter = new ArrayList<String>()) {
        log.info("Seed file (path=${path})")
        log.info("Project filter (filter=${projectFilter})")
        Project[] projects = filterProjects(this.reader.readFile(path), projectFilter)
        this.seed(projects)
    }

    /**
     * Template method for generating a seed, based on the
     * passed in projects configuration. See also the class documentation.
     *
     * @param projects
     */
    protected void seed(Project[] projects) {
        log.info("Merging projects")
        projects = this.merger.merge(projects)

        log.info("Resolving projects")
        this.resolver.resolve(projects)

        log.info("Creating model builder")
        IModelBuilder builder = this.buildCreator(projects)

        log.info("Building Jenkins model")
        IModel model = builder.build()

        log.info("Dispatching model for generation")
        this.dispatcher.dispatch(model)

        log.info("Seed application done")
    }
}
