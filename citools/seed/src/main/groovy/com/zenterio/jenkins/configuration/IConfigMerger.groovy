package com.zenterio.jenkins.configuration

interface IConfigMerger {

    public Project[] merge(Project[] projects);
}
