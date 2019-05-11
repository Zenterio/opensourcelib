package com.zenterio.jenkins

import com.zenterio.jenkins.configuration.TestContext

import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.BaseProduct
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.jobtype.JobType


class DisplayName {

    private final String identifier
    private final String SEPARATOR

    public DisplayName(String identifier = "") {
        this.identifier = identifier
        this.SEPARATOR = " "
    }

    protected result(List lst) {
        return lst.findAll({ it != "" }).join(this.SEPARATOR)
    }

    public String getName(Project project) {
        return this.result([project.name])
    }

    public String getName(Project project, Origin origin) {
        return this.result([
            project.name,
            origin.name,
            this.identifier
        ])
    }

    public String getName(Origin origin) {
        return getName(origin.getProject(), origin)
    }

    public String getName(Project project, Origin origin, BaseProduct product) {
        return this.result([
            project.name,
            origin.name,
            "flow",
            product.name,
            this.identifier
        ])
    }

    public String getName(BaseProduct product) {
        Origin o = product.getOrigin()
        Project p = o.getProject()
        return getName(p, o, product)
    }

    public String getName(Origin origin, JobType jobType) {
        Project project = origin.getProject()
        return getName(project, origin, jobType)
    }

    public String getName(BaseProduct product, JobType jobType, BuildType buildType) {
        Origin origin = product.getOrigin()
        Project project = origin.getProject()
        return getName(project, origin, product, jobType, buildType)
    }

    public String getName(Project project, JobType jobType) {
        return this.result([project.name, jobType.name])
    }

    public String getName(Project project, Origin origin, JobType jobType) {
        return this.result([
            project.name,
            origin.name,
            jobType.name
        ])
    }

    public String getName(Project project, Origin origin, BaseProduct product,
                    JobType jobType, BuildType buildType) {
        return this.result([
            project.name,
            origin.name,
            jobType.name,
            product.name,
            buildType.name
        ])
    }

    /**
     * Test runner jobs (test contexts)
     * @param product
     * @param jobType
     * @param buildType
     * @param testContext
     * @return
     */
    public String getName(BaseProduct product, JobType jobType, BuildType buildType, TestContext testContext) {
        return this.result([
                this.getName(product, jobType, buildType), testContext.testGroup.name, testContext.name
        ])
    }
}
