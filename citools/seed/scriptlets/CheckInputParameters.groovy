/**
 * Auto-generated script from template CheckInputParameters.groovy
 *
 * Check that all input parameters have reasonable values...
 */



// logic wrapped in closure to avoid polluting global scope
{ it ->
    def errors = []

    build.getBuildVariables().each {name, value ->
        if(!(name == "previous_git_tag_name")) {
            if(!value) {
                errors += "ERROR: Parameter ${name} must have a value..."
            }
        }
    }

    if(errors) {
        println('==================================')
        println(errors.join('\n'))
        println('==================================')
        println()
        return false
    }

    return true

}();
