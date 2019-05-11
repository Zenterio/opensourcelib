package com.zenterio.jenkins

import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.Product
import com.zenterio.jenkins.configuration.TestContext
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.jobtype.JobTypeIncrementalUnitTest
import com.zenterio.jenkins.jobtype.JobTypeUnitTest

class DescriptionDisplayName {

    public String getName(JobType jt, BuildType bt) {
        return bt.toString()
    }

    public String getName(JobTypeUnitTest jt, BuildType bt) {
        return "unit-test"
    }

    public String getName(JobTypeIncrementalUnitTest jt, BuildType bt) {
        return "unit-test"
    }

    public String getName(Product product) {
        return product.name
    }

    public String getName(TestContext context, BuildType bt) {
        return "${context.testGroup.name} ${context.name} (${bt.name})"
    }

}
