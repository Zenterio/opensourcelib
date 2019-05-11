package com.zenterio.jenkins.configuration


class FilterProjects {

    /**
     * @param projects
     * @param filter
     */
    public static Project[] filterProjects(Project[] projects, List<String> seedProjectFilter) {
        if (seedProjectFilter == null) {
            return projects
        }
        return projects.grep({ Project proj ->
            (seedProjectFilter.size == 0) || (proj.name in seedProjectFilter)
        }) as Project[]
    }

}
