package com.zenterio.jenkins.configuration

import groovy.util.logging.*

@Log
class SeedConfigMerger implements IConfigMerger {

    public SeedConfigMerger() {
    }

    @Override
    public Project[] merge(Project[] projects) {
        if (projects.size() == 0) {
            return projects
        }

        Project[] projectInfos = projectsWithoutOrigins(projects)
        def projectInfoNames = projectInfos.collect{ Project project -> project.name }

        if (!projectInfos) {
            String message = "Expecting at least one project-info, none was found."
            log.severe(message)
            throw new ConfigError(message)
        }

        if (projectInfoNames.unique(false).size() != projectInfoNames.size()) {
            String message = "Multiple project-infos with the same name is not allowed."
            log.severe(message)
            throw new ConfigError(message)
        }

        def projectNames = projectsWithOrigins(projects).collect{ Project project -> project.name }
        projectNames.each { String projectName ->
            if (!(projectName in projectInfoNames)) {
                String message = "Projects without a corresponding project-info is not allowed."
                log.severe(message)
                throw new ConfigError(message)
            }
        }

        projectInfos.each { Project projectInfo ->
            namedProjectsWithOrigins(projects, projectInfo.name).each { Project project ->
                projectInfo.addOrigins(project.origins)
            }
        }

        return projectInfos
    }

    private Project[] projectsWithoutOrigins(Project[] projects) {
        return projects.findAll{ Project project -> !project.origins }
    }

    private Project[] projectsWithOrigins(Project[] projects) {
        return projects.findAll{ Project project -> project.origins }
    }

    private Project[] namedProjectsWithOrigins(Project[] projects, String name) {
        return projects.findAll{ Project project -> project.name == name }
            .findAll{ Project project -> project.origins }
    }

}
