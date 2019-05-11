package com.zenterio.jenkins

import com.zenterio.jenkins.buildtype.*

class MakeBuildType {
    private String makeCmd
    private String dir
    private BuildType buildType

    MakeBuildType(BuildTypeDebug bt) {
        this.dir = bt.name
        this.makeCmd = ''
        this.buildType = bt
    }

    MakeBuildType(BuildTypeRelease bt) {
        this.dir = bt.name
        this.makeCmd = 'ZSYS_RELEASE=y'
        this.buildType = bt
    }

    MakeBuildType(BuildTypeProduction bt) {
        this.dir = bt.name
        this.makeCmd = 'ZSYS_PRODUCTION=y'
        this.buildType = bt
    }

    public String getMakeCmd() {
        return this.makeCmd
    }

    public String getDir() {
        return this.dir
    }

    public String getName() {
        return this.buildType.name
    }
}