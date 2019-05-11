package com.zenterio.jenkins.configuration

class SeedConfigMergerTest extends GroovyTestCase {

    SeedConfigMerger merger

    @Override
    protected void setUp() {
        this.merger = new SeedConfigMerger()
    }

    public void testMergingEmptyProjectListReturnsEmptyList() {
        Project[] result = this.merger.merge(new Project[0])
        assert result.size() == 0
    }

    public void testMergingProjectInfoWithProject() {
        Project projectInfo = Project.testData
        Project project = Project.testData
        projectInfo.origins = null

        Project[] mergedProjects = this.merger.merge([projectInfo, project] as Project[])
        assert mergedProjects.size() == 1
        assert mergedProjects[0].origins.size() == project.origins.size()
    }

    public void testMergingProjectInfoWithMultipleProjects() {
        Project projectInfo = Project.testData
        Project aProject = Project.testData
        Project anotherProject = Project.testData
        projectInfo.origins = null

        Project[] mergedProjects = this.merger.merge([projectInfo, aProject, anotherProject] as Project[])
        assert mergedProjects.size() == 1
        assert mergedProjects[0].origins.size() == aProject.origins.size() + anotherProject.origins.size()
    }

    public void testMissingProjectInfo() {
        Project project = Project.testData

        shouldFail(ConfigError) {
            this.merger.merge([project] as Project[])
        }
    }

    public void testMultipleProjectInfoWithTheSameName() {
        Project aProjectInfo = Project.testData
        Project anotherProjectInfo = Project.testData
        aProjectInfo.origins = null
        anotherProjectInfo.origins = null

        shouldFail(ConfigError) {
            this.merger.merge([aProjectInfo, anotherProjectInfo] as Project[])
        }
    }

    public void testDanglingProjectsLackingProjectInfo() {
        Project projectInfo = Project.testData
        Project project = Project.testData
        Project danglingProject = Project.testData
        projectInfo.name = "PROJECT-NAME"
        projectInfo.origins = null
        project.name = "PROJECT-NAME"
        danglingProject.name = "DANGLING-PROJECT-NAME"

        shouldFail(ConfigError) {
            this.merger.merge([projectInfo, project, danglingProject] as Project[])
        }
    }

}
