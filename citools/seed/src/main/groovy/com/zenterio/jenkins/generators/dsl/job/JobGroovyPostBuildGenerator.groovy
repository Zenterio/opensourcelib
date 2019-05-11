package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobGroovyPostBuildModel
import static com.zenterio.jenkins.generators.dsl.NodeUtils.getNodeContent
import static com.zenterio.jenkins.generators.dsl.NodeUtils.setNodeContent

import groovy.util.logging.*

/**
 * Generates Groovy Script Post Build Actions.
 * <p>
 * The generator supports multiple invocations, even through
 * multiple instances of the Generator, since it reads the entity's underlying
 * node structure; the generator instance itself is state-less.
 * <p>
 * There is no general structure in Groovy that can wrap a arbitrary section
 * of code to prevent variable and state clashes. E.g. classes cannot be defined
 * inside a code-block or closure, mechanisms otherwise used to wrap arbitrary
 * code. Therefore, each script are responsible to minimize its pollution in the
 * global scope as well as restoring any global state changed. Otherwise,
 * scripts that work in some contexts will start failing in other when combined
 * with other post build action scripts.
 */
@Log
class JobGroovyPostBuildGenerator implements IPropertyGenerator {


    public void generate(ModelProperty model, Object entity) {
        JobGroovyPostBuildModel m = (JobGroovyPostBuildModel) model

        /*
         * The script is wrapped in an identifier to make it easier
         * to see what script code belongs together.
         */
        String wrappedScript = """
// --- Script Start ---
${m.getScript()}
// --- Script End ---
"""
        String currentScript = getNodeContent(entity.node, 'publishers',
            'org.jvnet.hudson.plugins.groovypostbuild.GroovyPostbuildRecorder',
            'groovyScript')

        /*
         * This unfortunate setup is required because groovyPostBuild() creates
         * new nodes even if they already exists, resulting in multiple
         * entries if called multiple times.
         */
        if (currentScript == "") {
            entity.with {
                publishers {
                    groovyPostBuild {
                        script(wrappedScript)
                        sandbox(true)
                    }
                }
            }
        } else {
            String allScripts = "${currentScript}${wrappedScript}"
            setNodeContent(entity.node, allScripts,
                'publishers',
                'org.jvnet.hudson.plugins.groovypostbuild.GroovyPostbuildRecorder',
                'groovyScript')
        }
    }
}
