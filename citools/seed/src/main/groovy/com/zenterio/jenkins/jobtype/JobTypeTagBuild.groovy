package com.zenterio.jenkins.jobtype

public class JobTypeTagBuild extends JobType {

    public JobTypeTagBuild() {
        super("tag-build", "tag-build", "Helper job that tags the repositories involved in another jenkins build. There is one tag-build generated per project.")
    }
}
