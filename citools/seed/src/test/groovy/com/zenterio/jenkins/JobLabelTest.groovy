package com.zenterio.jenkins

import com.zenterio.jenkins.configuration.BuildNodeList
import com.zenterio.jenkins.configuration.BuildNode
import com.zenterio.jenkins.jobtype.JobTypeCompile
import com.zenterio.jenkins.jobtype.JobTypeIncrementalCompile
import com.zenterio.jenkins.jobtype.JobType

class JobLabelTest extends GroovyTestCase {

    public void testEmptyBuildNodeListGivesDefault() {
        JobType cpl = new JobTypeCompile()
        JobType inc = new JobTypeIncrementalCompile()
        BuildNodeList lst = new BuildNodeList()
        assert new JobLabel(cpl, lst).getLabel() == new JobLabel(cpl).getLabel()
        assert new JobLabel(inc, lst).getLabel() == new JobLabel(inc).getLabel()
    }

    public void testBuildNodeListTakesPriority() {
        JobType cpl = new JobTypeCompile()
        JobType inc = new JobTypeIncrementalCompile()
        BuildNodeList lst = [BuildNode.testData] as BuildNodeList
        assert new JobLabel(cpl, lst).getLabel() == lst.getLabelExpression()
        assert new JobLabel(inc, lst).getLabel() == lst.getLabelExpression()
    }

}
