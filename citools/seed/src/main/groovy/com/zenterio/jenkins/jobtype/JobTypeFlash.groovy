package com.zenterio.jenkins.jobtype

public class JobTypeFlash extends JobType {

    public JobTypeFlash() {
        super("flash", "flash", "Helper job that flashes an STB with an image. There is one flash job generated per project.")
    }
}
