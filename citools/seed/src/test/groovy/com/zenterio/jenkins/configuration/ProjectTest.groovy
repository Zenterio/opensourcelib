package com.zenterio.jenkins.configuration

class ProjectTest extends GroovyTestCase {

    public void testDeepClone() {
        Project project = Project.testData

        shouldFail(CloneNotSupportedException) {
            def clone = project.clone()
        }
    }

    public void testSetOrigins() {
        Project project = Project.testData
        project.origins = Origin.testData
        assert project.origins.size() == 1
        assert project.origins[0].project == project
    }

    public void testAddOrigins() {
        Project project = Project.testData
        project.origins = null
        project.addOrigins(Origin.testData as Origin[])
        project.addOrigins(Origin.testData as Origin[])
        assert project.origins.size() == 2
        assert project.origins[0].project == project
        assert project.origins[1].project == project
    }
}
