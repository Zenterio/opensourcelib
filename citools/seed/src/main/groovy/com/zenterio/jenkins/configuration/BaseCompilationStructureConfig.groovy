package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

/**
 * The purpose of this class is to hold all member variables that
 * are inherited across the configuration structure types.
 * This to reduce code duplication associated with all feature and
 * property configuration objects that need to be accessible across
 * all types.
 */
@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
abstract class BaseCompilationStructureConfig extends BaseStructureConfig {

    // Features
    Cache cache
    CsvDataPlot[] csvDataPlots

    // Properties
    BuildEnv buildEnv
    BuildNodeList buildNodes
    CredentialList credentials
    CustomBuildStepList customBuildSteps
    Description description
    Incremental incremental
    LogParsing logParsing
    MakePrefix makePrefix
    MakeRoot makeRoot
    MakeTarget makeTarget
    Repository[] repositories
    StartedBy startedBy
    SwUpgrades swUpgrades


    /**
     * Default constructor
     */
    public BaseCompilationStructureConfig() {
        super()
        this.csvDataPlots = new CsvDataPlot[0]

        this.buildEnv = null
        this.buildNodes = new BuildNodeList()
        this.cache = null
        this.credentials = new CredentialList()
        this.customBuildSteps = new CustomBuildStepList()
        this.description = null
        this.incremental = null
        this.logParsing = null
        this.makePrefix = null
        this.makeRoot = null
        this.makeTarget = null
        this.repositories = new Repository[0]
        this.startedBy = null
        this.swUpgrades = new SwUpgrades()
    }

    /**
     * Copy constructor
     * @param other
     */
    public BaseCompilationStructureConfig(BaseCompilationStructureConfig other) {
        super(other)
        this.csvDataPlots = other.csvDataPlots.collect{ it?.clone() } as CsvDataPlot[]
        this.buildEnv = other.buildEnv?.clone()
        this.buildNodes = other.buildNodes?.clone()
        this.cache = other.cache?.clone()
        this.credentials = other.credentials?.clone()
        this.customBuildSteps = other.customBuildSteps?.clone()
        this.description = other.description?.clone()
        this.logParsing = other.logParsing?.clone()
        this.makePrefix = other.makePrefix?.clone()
        this.makeRoot = other.makeRoot?.clone()
        this.makeTarget = other.makeTarget?.clone()
        this.repositories = other.repositories.collect { r -> r?.clone() } as Repository[]
        this.startedBy = other.startedBy?.clone()
        this.swUpgrades = other.swUpgrades?.clone()
        this.incremental = other.incremental?.clone()
    }

}
