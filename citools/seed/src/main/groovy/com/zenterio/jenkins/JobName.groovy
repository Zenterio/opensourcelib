package com.zenterio.jenkins

import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.BaseProduct
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.TestContext
import com.zenterio.jenkins.jobtype.JobType

import java.util.List


class JobName {

    /**
     * Custom identifier to be appended to some of the generated names.
     * Used for things like "incremental"
     */
    private final String identifier

    /**
     * Token that separates the different parts of the name.
     */
    private final String SEPARATOR

    /**
     * @param identifier    Custom identifier to be appended to some of the
     *                      names.
     */
    public JobName(String identifier = "") {
        this.identifier = identifier
        this.SEPARATOR = "-"
    }

    /**
     * Helper function that generates the actual result string.
     * @param lst
     * @return
     */
    private result(List lst) {
        return lst.findAll({ it != "" }).join(this.SEPARATOR)
    }

    /**
     * Project specific, project view.
     * @param project
     * @return
     */
    public String getName(Project project) {
        return this.result([project.name])
    }

    /**
     * Origin specific, origin flow
     * @param project
     * @param origin
     * @return
     */
    public String getName(Project project, Origin origin) {
        return this.result([
            project.name.toLowerCase(),
            origin.name.toLowerCase(),
            "master",
            this.identifier
        ])
    }

    /**
     * short form for project, origin
     * @param origin
     * @return
     */
    public String getName(Origin origin) {
        return getName(origin.getProject(), origin)
    }

    /**
     * Top job for product, product flow.
     * @param project
     * @param origin
     * @param product
     * @return
     */
    public String getName(Project project, Origin origin, BaseProduct product) {
        return this.result([
            project.name.toLowerCase(),
            origin.name.toLowerCase(),
            "flow",
            product.name,
            this.identifier
        ])
    }

    /**
     * Short form for project, origin, product
     * @param product
     * @return
     */
    public String getName(BaseProduct product) {
        Origin o = product.getOrigin()
        Project p = o.getProject()
        return getName(p, o, product)
    }

    /**
     * Used for origin specific non-compile jobs such as trigger jobs.
     * @param project
     * @param origin
     * @param jobType
     * @return
     */
    public String getName(Project project, Origin origin, JobType jobType) {
        return this.result([
            project.name.toLowerCase(),
            origin.name.toLowerCase(),
            jobType.shortName.toLowerCase(),
            this.identifier
        ])
    }

    /**
     * Short for fore project, origin, jobtype
     * @param origin
     * @param jobType
     * @return
     */
    public String getName(Origin origin, JobType jobType) {
        Project project = origin.getProject()
        return getName(project, origin, jobType)
    }

    /**
     * Used for project specific jobs such as tag jobs.
     * @param project
     * @param jobType
     * @return
     */
    public String getName(Project project, JobType jobType) {
        return this.result([
            project.name.toLowerCase(),
            jobType.shortName.toLowerCase()
        ])
    }


    /**
     *
     * @param project
     * @param origin
     * @param product
     * @param jobType
     * @param buildType
     * @return
     */
    public String getName(Project project, Origin origin, BaseProduct product,
                    JobType jobType, BuildType buildType) {
        return this.result([
            project.name.toLowerCase(),
            origin.name.toLowerCase(),
            jobType.shortName.toLowerCase(),
            product.name,
            buildType.shortName.toLowerCase()
        ])
    }

    /**
     * Short form for project, origin, product, jobtype, buildtype.
     * @param product
     * @param jobType
     * @param buildType
     * @return
     */
    public String getName(BaseProduct product, JobType jobType, BuildType buildType) {
        Origin origin = product.getOrigin()
        Project project = origin.getProject()
        return getName(project, origin, product, jobType, buildType)
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
