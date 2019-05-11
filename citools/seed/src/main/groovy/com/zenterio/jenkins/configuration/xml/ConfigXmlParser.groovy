package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.RetentionPolicy
import com.zenterio.jenkins.RetentionPolicyFactory
import com.zenterio.jenkins.RetentionPolicyType
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.buildtype.BuildTypeDebug
import com.zenterio.jenkins.buildtype.BuildTypeProduction
import com.zenterio.jenkins.buildtype.BuildTypeRelease
import com.zenterio.jenkins.configuration.*

import groovy.util.logging.Log

@Log
class ConfigXmlParser {

    public Project[] parseFile(String fileName) {
        XmlParser xmlParser = ValidatingXmlParserFactory.getXmlParser()
        Node parsedProjectXml = xmlParser.parse(new File(fileName))
        return (Project[]) parse(parsedProjectXml)
    }

    public Object parse(Node node) {
        switch (node.name()) {
            case "description":
                return this.parseDescription(node)
            case "projects":
                return this.parseProjects(node)
            case "project-info":
                return this.parseProject(node)
            case "project":
                return this.parseProject(node)
            case "origin":
                return this.parseOrigin(node)
            case "owner":
                return this.parseOwner(node)
            case "pm":
                return this.parseProjectManager(node)
            case "make-prefix":
                return this.parseMakePrefix(node)
            case "make-root":
                return this.parseMakeRoot(node)
            case "make-target":
                return this.parseMakeTarget(node)
            case "techlead":
                return this.parseTechLead(node)
            case "test-context":
                return this.parseTestContext(node)
            case "watcher":
                return this.parseWatcher(node)
            case "product":
                return this.parseProduct(node)
            case "resources":
                return this.parseResources(node)
            case "repository":
                return this.parseRepository(node)
            case "retention-policy":
                return this.parseRetentionPolicy(node)
            case "started-by":
                return this.parseStartedBy(node)
            case "sw-upgrade":
                return this.parseSwUpgrade(node)
            case "trigger":
                return this.parseTrigger(node)
            case "coverity":
                return this.parseCoverity(node)
            case "csv-data-plot":
                return this.parseCsvDataPlot(node)
            case "build-flow":
                return this.parseBuildFlow(node)
            case "inc-build-flow":
                return this.parseBuildFlow(node)
            case "build-env":
                return this.parseBuildEnv(node)
            case "build-node":
                return this.parseBuildNode(node)
            case "build-timeout":
                return this.parseBuildTimeout(node)
            case "cache":
                return this.parseCache(node)
            case "concurrent-builds":
                return this.parseConcurrentBuilds(node)
            case "credential":
                return this.parseCredential(node)
            case "custom-build-step":
                return this.parseCustomBuildStep(node)
            case "test-group":
                return this.parseTestGroup(node)
            case "doc":
                return this.parseDoc(node)
            case "duration":
                return this.parseDuration(node)
            case "epg":
                return this.parseEpg(node)
            case "image":
                return this.parseImage(node)
            case "incremental":
                return this.parseIncremental(node)
            case "jasmine":
                return this.parseJasmine(node)
            case "log-parsing":
                return this.parseLogParsing(node)
            case "test-command-args":
                return this.parseTestCommandArgs(node)
            case "test-job-input-parameter":
                return this.parseTestJobInputParameter(node)
            case "test-report":
                return this.parseTestReport(node)
            case "test-suite":
                return this.parseTestSuite(node)
            case "unit-test":
                return this.parseUnitTest(node)
            case "debug":
                return this.parseProductVariant(node)
            case "release":
                return this.parseProductVariant(node)
            case "production":
                return this.parseProductVariant(node)
            case "xml-to-csv":
                return this.parseXmlToCsv(node)
            case "xml-data":
                return this.parseXmlData(node)
            case "email-policy":
                return this.parseEmailPolicy(node)
            case "variable":
                return this.parseVariable(node)
            case "publish-build-over-ssh":
                return this.parsePublishBuildOverSSH(node)
            case "publish-over-ssh":
                return this.parsePublishOverSSH(node)
            case "publish-test-report-over-ssh":
                return this.parsePublishTestReportOverSSH(node)
            case "release-packaging":
                return this.parseReleasePackaging(node)
            case "workspace-browsing":
                return this.parseWorkspaceBrowsing(node)
            case "priority":
                return this.parsePriority(node)
            default:
                throw new ConfigError("Failed to parse (node=${node.name()})")
                break
        }
    }

    protected Boolean parseBooleanAttribute(Node node, String attributeName, Boolean defaultValue) {
        Boolean result
        if (node.attribute(attributeName) == null) {
            // if attribute not set in XML, use defaultValue
            result = defaultValue
        } else {
            // Handles conversion of string values.
            // True (case insensitive), 1, y
            // False (case insensitive), 0, n, --any other value
            result = ((String) node.attribute(attributeName))?.toBoolean()
        }
        return result
    }

    protected Boolean parseEnabledAttribute(Node node) {
        return parseBooleanAttribute(node, 'enabled', true)
    }

    protected String parseText(Node node) {
        return node.text().stripIndent().trim()
    }

    protected Project[] parseProjects(Node node) {
        def projects = []
        node.children().each({ Node child ->
            projects += parse(child)
        })
        return projects as Project[]
    }

    protected Project parseProject(Node node) {
        BuildFlow buildFlow = null
        BuildFlow incBuildFlow = null
        Coverity coverity = null
        PublishOverSSHList publishOverSSHList = new PublishOverSSHList()
        VariableCollection variables = new VariableCollection()
        ReleasePackaging releasePackaging = null
        def csvDataPlots = []
        Trigger trigger = null
        Description description = null
        Incremental incremental = null
        LogParsing logParsing = null
        MakePrefix makePrefix = null
        MakeRoot makeRoot = null
        MakeTarget makeTarget = null
        Doc doc = null
        Cache cache = null
        ConcurrentBuilds concurrentBuilds = null
        CredentialList credentials = new CredentialList()
        def cbss = new CustomBuildStepList()
        ProjectManager pm
        TechLead tl
        ContactInformationCollection watchers = new ContactInformationCollection()
        def origins = []
        ProductVariant debug = null
        ProductVariant release = null
        ProductVariant production = null
        SwUpgrades swUpgrades = new SwUpgrades()
        UnitTest unitTest = null
        BuildEnv buildEnv = null
        BuildNodeList buildNodes = new BuildNodeList()
        BuildTimeout buildTimeout = null
        RetentionPolicy retentionPolicy = null
        Resources resources = null
        StartedBy startedBy = null
        WorkspaceBrowsing workspaceBrowsing = null

        node.children().each({ Node child ->
            switch (child.name()) {
                case "build-flow":
                    buildFlow = parse(child)
                    break
                case "inc-build-flow":
                    incBuildFlow = parse(child)
                    break
                case "build-env":
                    buildEnv = parse(child)
                    break
                case "build-node":
                    buildNodes += parse(child)
                    break
                case "build-timeout":
                    buildTimeout = parse(child)
                    break
                case "description":
                    description = parse(child)
                    break
                case "incremental":
                    incremental = parse(child)
                    break
                case "cache":
                    cache = parse(child)
                    break
                case "concurrent-builds":
                    concurrentBuilds = parse(child)
                    break
                case "credential":
                    credentials += parse(child)
                    break
                case "custom-build-step":
                    cbss.add(parse(child))
                    break
                case "log-parsing":
                    logParsing = parse(child)
                    break
                case "make-prefix":
                    makePrefix = parse(child)
                    break
                case "make-root":
                    makeRoot = parse(child)
                    break
                case "make-target":
                    makeTarget = parse(child)
                    break
                case "pm":
                    pm = parse(child)
                    break
                case "resources":
                    resources = parse(child)
                    break
                case "retention-policy":
                    retentionPolicy = parse(child)
                    break
                case "techlead":
                    tl = parse(child)
                    break
                case "started-by":
                    startedBy = parse(child)
                    break
                case "unit-test":
                    unitTest = parse(child)
                    break
                case "watcher":
                    watchers += parse(child)
                    break
                case "origin":
                    origins += parse(child)
                    break
                case "sw-upgrade":
                    swUpgrades += parse(child)
                    break
                case "coverity":
                    coverity = parse(child)
                    break
                case "publish-build-over-ssh":
                case "publish-over-ssh":
                    publishOverSSHList += parse(child)
                    break
                case "release-packaging":
                    releasePackaging = parse(child)
                    break
                case "variable":
                    variables += parse(child)
                    break
                case "csv-data-plot":
                    csvDataPlots += parse(child)
                    break
                case "doc":
                    doc = parse(child)
                    break
                case "trigger":
                    trigger = parse(child)
                    break
                case "debug":
                    debug = parse(child)
                    break
                case "release":
                    release = parse(child)
                    break
                case "production":
                    production = parse(child)
                    break
                case "workspace-browsing":
                    workspaceBrowsing = parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to project (child=${child.name()})")
                    break
            }
        })
        String name = node.attribute('name')
        Project project = new Project(name, pm, tl,
                watchers, origins as Origin[])
        project.buildFlow = buildFlow
        project.description = description
        project.incBuildFlow = incBuildFlow
        project.incremental = incremental
        project.cache = cache
        project.concurrentBuilds = concurrentBuilds
        project.credentials = credentials
        project.customBuildSteps = cbss
        project.logParsing = logParsing
        project.makePrefix = makePrefix
        project.makeRoot = makeRoot
        project.makeTarget = makeTarget
        project.swUpgrades = swUpgrades
        project.coverity = coverity
        project.csvDataPlots = csvDataPlots as CsvDataPlot[]
        project.doc = doc
        project.trigger = trigger
        project.publishOverSSHList = publishOverSSHList
        project.releasePackaging = releasePackaging
        project.variables = variables
        project.debug = debug
        project.release = release
        project.production = production
        project.buildEnv = buildEnv
        project.buildNodes = buildNodes
        project.unitTest = unitTest
        project.buildTimeout = buildTimeout
        project.resources = resources
        project.retentionPolicy = retentionPolicy
        project.startedBy = startedBy
        project.workspaceBrowsing = workspaceBrowsing
        return project
    }

    protected Origin parseOrigin(Node node) {
        ContactInformationCollection watchers = new ContactInformationCollection()
        Boolean configurable = parseBooleanAttribute(node, "configurable", false)
        Boolean tagScm = parseBooleanAttribute(node, "tag-scm", true)
        def products = []
        def repositories = []
        LogParsing logParsing = null
        MakePrefix makePrefix = null
        MakeRoot makeRoot = null
        MakeTarget makeTarget = null
        ProjectManager pm = null
        TechLead tl = null
        Trigger trigger = null
        Doc doc = null
        Coverity coverity = null
        BuildFlow buildFlow = null
        BuildFlow incBuildFlow = null
        PublishOverSSHList publishOverSSHList = new PublishOverSSHList()
        VariableCollection variables = new VariableCollection()
        ReleasePackaging releasePackaging = null
        def csvDataPlots = []
        Cache cache = null
        ConcurrentBuilds concurrentBuilds = null
        CredentialList credentials = new CredentialList()
        def cbss = new CustomBuildStepList()
        Description description = null
        Incremental incremental = null
        ProductVariant debug = null
        ProductVariant release = null
        ProductVariant production = null
        SwUpgrades swUpgrades = new SwUpgrades()
        UnitTest unitTest = null
        BuildEnv buildEnv = null
        BuildNodeList buildNodes = new BuildNodeList()
        BuildTimeout buildTimeout = null
        Resources resources = null
        RetentionPolicy retentionPolicy = null
        StartedBy startedBy = null
        WorkspaceBrowsing workspaceBrowsing = null
        Priority priority = null

        node.children().each({ Node child ->
            switch (child.name()) {
                case "build-flow":
                    buildFlow = parse(child)
                    break
                case "inc-build-flow":
                    incBuildFlow = parse(child)
                    break
                case "build-env":
                    buildEnv = parse(child)
                    break
                case "build-node":
                    buildNodes += parse(child)
                    break
                case "build-timeout":
                    buildTimeout = parse(child)
                    break
                case "log-parsing":
                    logParsing = parse(child)
                    break
                case "make-prefix":
                    makePrefix = parse(child)
                    break
                case "make-root":
                    makeRoot = parse(child)
                    break
                case "make-target":
                    makeTarget = parse(child)
                    break
                case "pm":
                    pm = parse(child)
                    break
                case "retention-policy":
                    retentionPolicy = parse(child)
                    break
                case "started-by":
                    startedBy = parse(child)
                    break
                case "techlead":
                    tl = parse(child)
                    break
                case "watcher":
                    watchers += parse(child)
                    break
                case "product":
                    products += parse(child)
                    break
                case "repository":
                    repositories += parse(child)
                    break
                case "sw-upgrade":
                    swUpgrades += parse(child)
                    break
                case "unit-test":
                    unitTest = parse(child)
                    break
                case "coverity":
                    coverity = parse(child)
                    break
                case "csv-data-plot":
                    csvDataPlots += parse(child)
                    break
                case "doc":
                    doc = parse(child)
                    break
                case "trigger":
                    trigger = parse(child)
                    break
                case "publish-build-over-ssh":
                case "publish-over-ssh":
                    publishOverSSHList += parse(child)
                    break
                case "resources":
                    resources = parse(child)
                    break
                case "variable":
                    variables += parse(child)
                    break
                case "release-packaging":
                    releasePackaging = parse(child)
                    break
                case "description":
                    description = parse(child)
                    break
                case "incremental":
                    incremental = parse(child)
                    break
                case "cache":
                    cache = parse(child)
                    break
                case "concurrent-builds":
                    concurrentBuilds = parse(child)
                    break
                case "credential":
                    credentials += parse(child)
                    break
                case "custom-build-step":
                    cbss.add(parse(child))
                    break
                case "debug":
                    debug = parse(child)
                    break
                case "release":
                    release = parse(child)
                    break
                case "production":
                    production = parse(child)
                    break
                case "workspace-browsing":
                    workspaceBrowsing = parse(child)
                    break
                case "priority":
                    priority = parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to Origin (child=${child.name()})")
            }
        })
        Origin origin = new Origin(node.attributes()['name'],
                configurable,
                tagScm,
                products as Product[],
                repositories as Repository[],
                watchers)
        origin.logParsing = logParsing
        origin.makePrefix = makePrefix
        origin.makeRoot = makeRoot
        origin.makeTarget = makeTarget
        origin.pm = pm
        origin.techLead = tl
        origin.swUpgrades = swUpgrades
        origin.buildFlow = buildFlow
        origin.incBuildFlow = buildFlow
        origin.coverity = coverity
        origin.csvDataPlots = csvDataPlots as CsvDataPlot[]
        origin.doc = doc
        origin.trigger = trigger
        origin.publishOverSSHList = publishOverSSHList
        origin.variables = variables
        origin.releasePackaging = releasePackaging
        origin.description = description
        origin.incremental = incremental
        origin.cache = cache
        origin.concurrentBuilds = concurrentBuilds
        origin.credentials = credentials
        origin.customBuildSteps = cbss
        origin.debug = debug
        origin.release = release
        origin.production = production
        origin.unitTest = unitTest
        origin.buildEnv = buildEnv
        origin.buildNodes = buildNodes
        origin.buildTimeout = buildTimeout
        origin.resources = resources
        origin.retentionPolicy = retentionPolicy
        origin.startedBy = startedBy
        origin.workspaceBrowsing = workspaceBrowsing
        origin.priority = priority

        return origin
    }

    protected Coverity parseCoverity(Node node) {
        CustomBuildStepList cbss = new CustomBuildStepList()
        String stream = node.attribute('stream')
        Boolean enabled = parseEnabledAttribute(node)
        Upstream upstream = parseUpstreamAttribute(node)
        String periodic = node.attribute('periodic')
        Aggressiveness aggressiveness = parseAggressivenessAttribute(node)
        BuildType buildType = parseBuildTypeAttribute(node)
        PublishOverSSHList publishOverSSHList = []
        VariableCollection variables = new VariableCollection()
        BuildTimeout buildTimeout = null
        WorkspaceBrowsing workspaceBrowsing = null
        CredentialList credentials = new CredentialList()
        Resources resources = null
        BuildEnv buildEnv = null

        node.children().each({ Node child ->
            switch (child.name()) {
                case "build-env":
                    buildEnv = parse(child)
                    break
                case "build-timeout":
                    buildTimeout = parse(child)
                    break
                case "credential":
                    credentials += parse(child)
                    break
                case "custom-build-step":
                    cbss.add(parse(child))
                    break
                case "publish-over-ssh":
                    publishOverSSHList += parse(child)
                    break
                case "resources":
                    resources = parse(child)
                    break
                case "variable":
                    variables += parse(child)
                    break
                case "workspace-browsing":
                    workspaceBrowsing = parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to Coverity (child=${child.name()})")
            }
        })
        Coverity cov = new Coverity(stream, enabled, upstream, periodic, aggressiveness, buildType)
        cov.customBuildSteps = cbss
        cov.publishOverSSHList = publishOverSSHList
        cov.variables = variables
        cov.buildTimeout = buildTimeout
        cov.workspaceBrowsing = workspaceBrowsing
        cov.credentials = credentials
        cov.resources = resources
        cov.buildEnv = buildEnv
        return cov
    }

    protected Upstream parseUpstreamAttribute(Node node) {
        String upstreamStr = node.attribute('upstream')
        Upstream upstream
        switch (upstreamStr) {
            case "true":
                upstream = Upstream.TRUE
                break
            case "false":
                upstream = Upstream.FALSE
                break
            case "async":
                upstream = Upstream.ASYNC
                break
            case null:
                upstream = Upstream.TRUE
                break
            default:
                throw new ConfigError("Bad upstream attribute (${upstreamStr}), should be true, false or async")
        }
        return upstream
    }

    protected Aggressiveness parseAggressivenessAttribute(Node node) {
        String aggressivenessStr = node.attribute('aggressiveness-level')
        Aggressiveness aggressiveness
        switch (aggressivenessStr) {
            case "low":
                aggressiveness = Aggressiveness.LOW
                break
            case "medium":
                aggressiveness = Aggressiveness.MEDIUM
                break
            case "high":
                aggressiveness = Aggressiveness.HIGH
                break
            case null:
                aggressiveness = Aggressiveness.LOW
                break
            default:
                throw new ConfigError("Bad aggressiveness attribute (${aggressivenessStr}), should be low, medium or high")
        }
        return aggressiveness
    }

    protected BuildType parseBuildTypeAttribute(Node node) {
        String buildTypeStr = node.attribute('build-type')
        BuildType buildType
        switch (buildTypeStr) {
            case "debug":
                buildType = new BuildTypeDebug()
                break
            case "production":
                buildType = new BuildTypeProduction()
                break
            case "release":
                buildType = new BuildTypeRelease()
                break
            case null:
                buildType = new BuildTypeDebug()
                break
            default:
                throw new ConfigError("Bad buildType (${buildTypeStr}), should be debug, production or release")
        }
        return buildType
    }

    protected CsvDataPlot parseCsvDataPlot(Node node) {
        String input = node.attribute('input')
        String title = node.attribute('title')
        String group = node.attribute('group')
        String scale = node.attribute('scale')
        Double yMin = node.attribute('y-min') as Double
        Double yMax = node.attribute('y-max') as Double
        CsvDataPlotStyle style = CsvDataPlotStyle.getFromString(node.attribute('style'))
        Boolean enabled = parseEnabledAttribute(node)
        return new CsvDataPlot(input, title, group, scale, yMin, yMax, style, enabled)
    }

    protected XmlToCsv parseXmlToCsv(Node node) {
        String input = node.attribute('input')
        String output = node.attribute('output')
        List<XmlData> data = new ArrayList<XmlData>()
        node.children().each({ Node child ->
            switch (child.name()) {
                case "xml-data":
                    data.add(parse(child))
                    break
                default:
                    throw new ConfigError("Unexpect child node to xml-to-csv (child=${child.name()})")
            }
        })
        return new XmlToCsv(input, output, data as XmlData[])
    }

    protected XmlData parseXmlData(Node node) {
        String source = node.attribute('source')
        XmlDataOperation operation = XmlDataOperation.getFromString(node.attribute('operation'))
        String field = node.attribute('field')
        String caption = node.attribute('caption')
        return new XmlData(source, operation, field, caption)
    }

    protected TestGroup parseTestGroup(Node node) {
        List<Epg> epgs = new ArrayList<Epg>()
        Image image = null
        LogParsing logParsing = null
        List<Repository> repositories = new ArrayList<Repository>()
        List<TestContext> testContexts = new ArrayList<TestContext>()
        String name = node.attribute('name')
        TestGroupType type = TestGroupType.valueOf(node.attribute('type').toUpperCase())
        CredentialList credentials = new CredentialList()
        def cbss = new CustomBuildStepList()
        Description description = null
        String testRoot = node.attribute('test-root')
        String stbLabel = node.attribute('stb-label')
        String boxConfiguration = node.attribute('box-configuration')
        String productConfiguration = node.attribute('product-configuration')
        Boolean coredumpHandling = parseBooleanAttribute(node, "coredump-handling", true)
        Boolean enabled = parseEnabledAttribute(node)
        ContactInformationCollection watchers = new ContactInformationCollection()
        PublishOverSSHList publishOverSSHList = []
        BuildTimeout buildTimeout = null
        Resources resources = null
        RetentionPolicy retentionPolicy = null
        TestReport testReport = null
        WorkspaceBrowsing workspaceBrowsing = null
        VariableCollection variables = new VariableCollection()

        node.children().each({ Node child ->
            switch (child.name()) {
                case "build-timeout":
                    buildTimeout = parse(child)
                    break
                case "credential":
                    credentials += parse(child)
                    break
                case "custom-build-step":
                    cbss.add(parse(child))
                    break
                case "description":
                    description = parse(child)
                    break
                case "epg":
                    epgs.add(parse(child))
                    break
                case "image":
                    image = parse(child)
                    break
                case "repository":
                    repositories.add(parse(child))
                    break
                case "test-context":
                    testContexts.add(parse(child))
                    break
                case "resources":
                    resources = parse(child)
                    break
                case "variable":
                    variables += parse(child)
                    break
                case "watcher":
                    watchers.add(parse(child))
                    break
                case "log-parsing":
                    logParsing = parse(child)
                    break
                case "publish-over-ssh":
                case "publish-test-report-over-ssh":
                    publishOverSSHList += parse(child)
                    break
                case "retention-policy":
                    retentionPolicy = parse(child)
                    break
                case "test-report":
                    testReport = parse(child)
                    break
                case "workspace-browsing":
                    workspaceBrowsing = parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to test-group (child=${child.name()})")
            }
        })

        TestGroup testGroup = new TestGroup(name, type, description, testRoot, stbLabel,
                boxConfiguration, productConfiguration, repositories as Repository[], testContexts as TestContext[],
                image, logParsing, enabled, coredumpHandling, epgs as Epg[], watchers)
        testGroup.publishOverSSHList = publishOverSSHList
        testGroup.buildTimeout = buildTimeout
        testGroup.credentials = credentials
        testGroup.customBuildSteps = cbss
        testGroup.resources = resources
        testGroup.retentionPolicy = retentionPolicy
        testGroup.testReport = testReport
        testGroup.workspaceBrowsing = workspaceBrowsing
        testGroup.variables = variables
        return testGroup
    }

    protected ConfigAction parseActionAttribute(Node node) {
        String actionStr = node.attribute('action')
        ConfigAction action = null
        switch (actionStr) {
            case "manual":
                action = ConfigAction.MANUAL
                break
            case "automatic":
                action = ConfigAction.AUTOMATIC
                break
            case null:
                action = null
                break
            default:
                throw new ConfigError("Bad action (${actionStr}), should be manual or automatic.")
        }
        return action
    }

    protected EmailPolicyWhen parseEmailPolicyWhen(String policyString) {
        if (policyString == null) {
            return null
        } else {
            return policyString.toUpperCase() as EmailPolicyWhen
        }
    }

    protected EmailPolicy parseEmailPolicy(Node node) {
        EmailPolicyWhen slowFeedback = parseEmailPolicyWhen(node.attribute("slow-feedback"))
        EmailPolicyWhen fastFeedback = parseEmailPolicyWhen(node.attribute("fast-feedback"))
        EmailPolicyWhen utility = parseEmailPolicyWhen(node.attribute("utility"))
        EmailPolicyWhen test = parseEmailPolicyWhen(node.attribute('test'))
        return new EmailPolicy(slowFeedback, fastFeedback, utility, test)
    }

    protected Doc parseDoc(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        Doc doc = new Doc(enabled)
        node.children().each({ Node child ->
            switch (child.name()) {
                case "build-env":
                    doc.buildEnv = parse(child)
                    break
                case "build-timeout":
                    doc.buildTimeout = parse(child)
                    break
                case "credential":
                    doc.credentials += parse(child)
                    break
                case "custom-build-step":
                    doc.customBuildSteps += parse(child)
                    break
                case "make-prefix":
                    doc.makePrefix = parse(child)
                    break
                case "make-root":
                    doc.makeRoot = parse(child)
                    break
                case "make-target":
                    doc.makeTarget = parse(child)
                    break
                case "publish-build-over-ssh":
                case "publish-over-ssh":
                    doc.publishOverSSHList += parse(child)
                    break
                case "resources":
                    doc.resources = parse(child)
                    break
                case "variable":
                    doc.variables += parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to ${node.name()} (child=${child.name()})")
            }
        })
        return doc
    }

    protected UnitTest parseUnitTest(Node node) {
        Boolean builtIn = parseBooleanAttribute(node, "built-in", true)
        Boolean enabled = parseEnabledAttribute(node)

        def csvDataPlots = []
        UnitTest unitTest = new UnitTest(builtIn, enabled)

        node.children().each({ Node child ->

            if (builtIn) {
                log.warning("Unit-test child-node ${child.name()} will be ignored due to attribute built-in=true")
            }
            switch (child.name()) {
                case "build-env":
                    unitTest.buildEnv = parse(child)
                    break
                case "build-timeout":
                    unitTest.buildTimeout = parse(child)
                    break
                case "credential":
                    unitTest.credentials += parse(child)
                    break
                case "csv-data-plot":
                    csvDataPlots += parse(child)
                    break
                case "publish-over-ssh":
                    unitTest.publishOverSSHList += parse(child)
                    break
                case "resources":
                    unitTest.resources = parse(child)
                    break
                case "variable":
                    unitTest.variables += parse(child)
                    break
                case "custom-build-step":
                    unitTest.customBuildSteps += parse(child)
                    break
                case "description":
                    unitTest.description = parse(child)
                    break
                case "log-parsing":
                    unitTest.logParsing = parse(child)
                    break
                case "make-prefix":
                    unitTest.makePrefix = parse(child)
                    break
                case "make-root":
                    unitTest.makeRoot = parse(child)
                    break
                case "make-target":
                    unitTest.makeTarget = parse(child)
                    break
                case "watcher":
                    unitTest.watchers += parse(child)
                    break
                case "workspace-browsing":
                    unitTest.workspaceBrowsing = parse(child)
                    break
                case "cache":
                    unitTest.cache = parse(child)
                    break
                case "credential":
                    unitTest.credentials += parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to unit-test (child=${child.name()})")
            }
        })
        unitTest.csvDataPlots = csvDataPlots as CsvDataPlot[]
        return unitTest
    }

    protected BuildEnv parseBuildEnv(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        String env = node.attributes()["env"]
        String args = node.attributes()["args"]
        return new BuildEnv(enabled, env, args)
    }

    protected BuildFlow parseBuildFlow(Node node) {
        return new BuildFlow(this.parseBuildFlowStyleAttribute(node))
    }

    protected BuildFlowStyle parseBuildFlowStyleAttribute(Node node) {
        String style = node.attributes()["style"]
        switch (style) {
            case "zids-unit-test-built-in":
                return BuildFlowStyle.ZIDS_UNIT_TEST_BUILT_IN
            case "zids-unit-test-serial":
                return BuildFlowStyle.ZIDS_UNIT_TEST_SERIAL
            case "zids-unit-test-parallel":
                return BuildFlowStyle.ZIDS_UNIT_TEST_PARALLEL
            default:
                throw new ConfigError("Unexpected build-flow style (style=${style})")
        }
    }

    protected Description parseDescription(Node node) {
        return new Description(parseText(node))
    }

    protected Incremental parseIncremental(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        Incremental incremental = new Incremental(enabled)
        node.children().each({ Node child ->
            switch (child.name()) {
                case "cache":
                    incremental.cache = parse(child)
                    break
                case "test-group":
                    incremental.testGroups += parse(child)
                    break
                case "resources":
                    incremental.resources = parse(child)
                    break
                case "variable":
                    incremental.variables += parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to ${node.name()} (child=${child.name()})")
            }
        })
        return incremental
    }

    protected BuildNode parseBuildNode(Node node) {
        String label = node.attribute('label')
        return new BuildNode(label)
    }

    protected BuildTimeout parseBuildTimeout(Node node) {
        String policyString = node.attribute('policy')
        BuildTimeoutPolicy policy = null
        Integer minutes = node.attributes()["minutes"] as Integer
        Boolean failBuild = parseBooleanAttribute(node, 'fail-build', false)
        Boolean configurable = parseBooleanAttribute(node, 'configurable', false)
        Boolean enabled = parseEnabledAttribute(node)

        switch (policyString) {
            case "absolute":
                policy = BuildTimeoutPolicy.ABSOLUTE
                break
            case "elastic":
                policy = BuildTimeoutPolicy.ELASTIC
                break
            default:
                if (enabled) {
                    throw new ConfigError("Bad policy (${policyString}), should be disabled, elastic or noactivity")
                }
        }
        return new BuildTimeout(policy, minutes, failBuild, configurable, enabled)
    }

    protected CustomBuildStep parseCustomBuildStep(Node node) {
        String modeString = node.attribute('mode')
        String typeString = node.attribute('type')
        String overrideName = node.attribute('override-name')
        CustomBuildStepMode mode = null
        Boolean enabled = parseEnabledAttribute(node)
        CustomBuildStepType type = null

        switch (typeString) {
            case "shell":
                type = CustomBuildStepType.SHELL
                break
            case "system-groovy":
                type = CustomBuildStepType.SYSTEM_GROOVY
                break
            case null:
                type = null
                break
            default:
                throw new ConfigError("Bad custom build step type (${typeString}), should be ${CustomBuildStepType.values().join(' or ')}")
        }

        switch (modeString) {
            case "prepend":
                mode = CustomBuildStepMode.PREPEND
                break
            case "append":
                mode = CustomBuildStepMode.APPEND
                break
            case "override":
                mode = CustomBuildStepMode.OVERRIDE
                break
            case "override-named":
                mode = CustomBuildStepMode.OVERRIDE_NAMED
                break
            case null:
                mode = null
                break
            default:
                throw new ConfigError("Bad custom build step mode (${modeString}), should be prepend, append, override or override-named")
        }
        return new CustomBuildStep(parseText(node), mode, enabled, type, overrideName)
    }

    protected MakePrefix parseMakePrefix(Node node) {
        return new MakePrefix(node.attribute("value"))
    }

    protected MakeRoot parseMakeRoot(Node node) {
        return new MakeRoot(node.attribute("name"))
    }

    protected MakeTarget parseMakeTarget(Node node) {
        return new MakeTarget(node.attribute("name"))
    }

    protected ProjectManager parseProjectManager(Node node) {
        ContactInformation contactInformation = parsecContactInformation(node)
        return new ProjectManager(contactInformation.name, contactInformation.email, contactInformation.emailPolicy)
    }

    protected TechLead parseTechLead(Node node) {
        ContactInformation contactInformation = parsecContactInformation(node)
        return new TechLead(contactInformation.name, contactInformation.email, contactInformation.emailPolicy)
    }

    protected Watcher parseWatcher(Node node) {
        ContactInformation contactInformation = parsecContactInformation(node)
        return new Watcher(contactInformation.name, contactInformation.email, contactInformation.emailPolicy)
    }

    protected Owner parseOwner(Node node) {
        ContactInformation contactInformation = parsecContactInformation(node)
        String group = node.attributes()['group']
        return new Owner(contactInformation.name, contactInformation.email, contactInformation.emailPolicy, group)
    }

    protected ContactInformation parsecContactInformation(Node node) {
        String name = node.attributes()['name']
        String email = node.attributes()['email']
        EmailPolicy emailPolicy = null
        node.children().each({ Node child ->
            switch (child.name()) {
                case "email-policy":
                    emailPolicy = parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to ${node.name()} (child=${child.name()})")
            }
        })
        return new ContactInformation(name, email, emailPolicy)
    }

    protected TestContext parseTestContext(Node node) {
        String name = node.attribute('name')
        def csvDataPlots = []
        def cbss = new CustomBuildStepList()
        Description description = null
        Duration duration = null
        LogParsing logParsing = null
        List<Epg> epgs = new ArrayList<Epg>()
        Image image = null
        List<TestSuite> testSuites = new ArrayList<TestSuite>()
        Upstream upstream = parseUpstreamAttribute(node)
        String polling = node.attribute('polling')
        String periodic = node.attribute('periodic')
        String stbLabel = node.attribute('stb-label')
        CredentialList credentials = new CredentialList()
        Boolean coredumpHandling = parseBooleanAttribute(node, "coredump-handling", null)
        Boolean enabled = parseEnabledAttribute(node)
        List<TestJobInputParameter> inputParameters = new ArrayList<TestJobInputParameter>()
        TestCommandArgs testCommandArgs = null
        ContactInformationCollection watchers = new ContactInformationCollection()
        def xmlToCsvs = []
        PublishOverSSHList publishOverSSHList = new PublishOverSSHList()
        BuildTimeout buildTimeout = null
        ContactInformationCollection owners = new ContactInformationCollection()
        List<Repository> repositories = new ArrayList<Repository>()
        RetentionPolicy retentionPolicy = null
        TestReport testReport = null
        Jasmine jasmine = null
        WorkspaceBrowsing workspaceBrowsing = null
        Resources resources = null
        VariableCollection variables = new VariableCollection()


        node.children().each({ Node child ->
            switch (child.name()) {
                case "build-timeout":
                    buildTimeout = parse(child)
                    break
                case "credential":
                    credentials += parse(child)
                    break
                case "csv-data-plot":
                    csvDataPlots += parse(child)
                    break
                case "custom-build-step":
                    cbss.add(parse(child))
                    break
                case "description":
                    description = parse(child)
                    break
                case "duration":
                    duration = parse(child)
                    break
                case "epg":
                    epgs.add(parse(child))
                    break
                case "image":
                    image = parse(child)
                    break
                case "jasmine":
                    jasmine = parse(child)
                    break
                case "test-job-input-parameter":
                    inputParameters.add(parse(child))
                    break
                case "test-command-args":
                    testCommandArgs = parse(child)
                    break
                case "test-report":
                    testReport = parse(child)
                    break
                case "test-suite":
                    testSuites.add(parse(child))
                    break
                case "owner":
                    owners.add(parse(child))
                    break
                case "repository":
                    repositories.add(parse(child))
                    break
                case "resources":
                    resources = parse(child)
                    break
                case "variable":
                    variables += parse(child)
                    break
                case "watcher":
                    watchers.add(parse(child))
                    break
                case "xml-to-csv":
                    xmlToCsvs += parse(child)
                    break
                case "log-parsing":
                    logParsing = parse(child)
                    break
                case "publish-over-ssh":
                case "publish-test-report-over-ssh":
                    publishOverSSHList += parse(child)
                    break
                case "retention-policy":
                    retentionPolicy = parse(child)
                    break
                case "workspace-browsing":
                    workspaceBrowsing = parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to test-context (child=${child.name()})")
            }
        })

        TestContext testContext = new TestContext(name, csvDataPlots as CsvDataPlot[],
                description, duration, testSuites as TestSuite[],
                upstream, polling, periodic, enabled,
                coredumpHandling, epgs as Epg[], image, logParsing, repositories as Repository[], watchers,
                inputParameters as TestJobInputParameter[],
                testCommandArgs, xmlToCsvs as XmlToCsv[])
        testContext.publishOverSSHList = publishOverSSHList
        testContext.buildTimeout = buildTimeout
        testContext.credentials = credentials
        testContext.customBuildSteps = cbss
        testContext.retentionPolicy = retentionPolicy
        testContext.jasmine = jasmine
        testContext.owners = owners
        testContext.workspaceBrowsing = workspaceBrowsing
        testContext.stbLabel = stbLabel
        testContext.resources = resources
        testContext.testReport = testReport
        testContext.variables = variables
        return testContext
    }

    protected Jasmine parseJasmine(Node node) {
        return new Jasmine(node.attribute('repository') as String,
                node.attribute('config-file') as String,
                node.attribute('url') as String,
                parseBooleanAttribute(node, 'disable-rcu', true),
                parseBooleanAttribute(node, 'disable-rcu-check', true))
    }

    protected Duration parseDuration(Node node) {
        return new Duration(node.attribute('time'))
    }

    protected Epg parseEpg(Node node) {
        return new Epg(node.attribute('path'))
    }

    protected Image parseImage(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        Boolean flatten = parseBooleanAttribute(node, 'flatten', true)
        return new Image(node.attribute('artifact'), enabled, flatten)
    }

    protected LogParsing parseLogParsing(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        return new LogParsing(node.attribute('config'), enabled)
    }

    protected TestSuite parseTestSuite(Node node) {
        return new TestSuite(node.attribute('path'))
    }

    protected TestReport parseTestReport(Node node) {
        String typeString = node.attribute('type')
        TestReportType type = null

        switch (typeString) {
            case "junit":
                type = TestReportType.JUNIT
                break
            case "testng":
                type = TestReportType.TESTNG
                break
            default:
                throw new ConfigError("Bad test report type (${typeString}), should be ${TestReportType.values().join(' or ')}")
        }

        return new TestReport(type)
    }

    protected ProductVariant parseProductVariant(Node node) {
        Boolean enabled = this.parseEnabledAttribute(node)
        BuildType buildType = this.parseBuildTypeAttribute(node)
        ProductVariant prodVariant = new ProductVariant(buildType, enabled)
        this.parseAndUpdateProductVariant(node, prodVariant)
        return prodVariant
    }

    protected TestCommandArgs parseTestCommandArgs(Node node) {
        return new TestCommandArgs(node.attribute('value'))
    }

    protected TestJobInputParameter parseTestJobInputParameter(Node node) {
        return new TestJobInputParameter(node.attribute('name'),
                node.attribute('default'), node.attribute('description'))
    }

    protected parseAndUpdateProductVariant(Node node, ProductVariant prodVariant) {
        def repositories = []
        ContactInformationCollection watchers = new ContactInformationCollection()
        def tests = []
        def csvDataPlots = []
        BuildEnv buildEnv = null
        Cache cache = null
        CredentialList credentials = new CredentialList()
        def customBuildSteps = []
        PublishOverSSHList publishOverSSHList = []
        Resources resources = null
        VariableCollection variables = new VariableCollection()
        BuildNodeList buildNodes = new BuildNodeList()
        BuildTimeout buildTimeout = null
        WorkspaceBrowsing workspaceBrowsing = null

        node.children().each({ Node child ->
            switch (child.name()) {
                case "build-env":
                    buildEnv = parse(child)
                    break
                case "build-node":
                    buildNodes += parse(child)
                    break
                case "build-timeout":
                    buildTimeout = parse(child)
                    break
                case "csv-data-plot":
                    csvDataPlots += parse(child)
                    break
                case "test-group":
                    tests += parse(child)
                    break
                case "publish-build-over-ssh":
                case "publish-over-ssh":
                    publishOverSSHList += parse(child)
                    break
                case "resources":
                    resources = parse(child)
                    break
                case "variable":
                    variables += parse(child)
                    break
                case "sw-upgrade":
                    prodVariant.swUpgrades += parse(child)
                    break
                case "custom-build-step":
                    customBuildSteps += parse(child)
                    break
                case "description":
                    prodVariant.description = parse(child)
                    break
                case "incremental":
                    prodVariant.incremental = parse(child)
                    break
                case "log-parsing":
                    prodVariant.logParsing = parse(child)
                    break
                case "make-prefix":
                    prodVariant.makePrefix = parse(child)
                    break
                case "make-root":
                    prodVariant.makeRoot = parse(child)
                    break
                case "make-target":
                    prodVariant.makeTarget = parse(child)
                    break
                case "pm":
                    prodVariant.pm = parse(child)
                    break
                case "repository":
                    repositories += parse(child)
                    break
                case "techlead":
                    prodVariant.techLead = parse(child)
                    break
                case "watcher":
                    watchers += parse(child)
                    break
                case "workspace-browsing":
                    workspaceBrowsing = parse(child)
                    break
                case "cache":
                    cache = parse(child)
                    break
                case "credential":
                    credentials += parse(child)
                    break
                default:
                /* Do nothing.
                 * This is a general parse function.
                 * It can be used by subclasses to ProductVariant as well
                 * which have additional nodes that ProductVariant knows nothing about.
                 */
                    break
            }
        })
        prodVariant.csvDataPlots = csvDataPlots as CsvDataPlot[]
        prodVariant.testGroups = tests as TestGroup[]
        prodVariant.repositories = repositories as Repository[]
        prodVariant.watchers = watchers
        prodVariant.buildEnv = buildEnv
        prodVariant.cache = cache
        prodVariant.credentials = credentials
        prodVariant.customBuildSteps = customBuildSteps as CustomBuildStep[]
        prodVariant.resources = resources
        prodVariant.variables = variables
        prodVariant.publishOverSSHList = publishOverSSHList
        prodVariant.buildNodes = buildNodes
        prodVariant.buildTimeout = buildTimeout
        prodVariant.workspaceBrowsing = workspaceBrowsing
    }

    protected Product parseProduct(Node node) {
        Product prod = new Product(node.attributes()['name'], node.attributes()['alt-name'])
        def csvDataPlots = []

        node.children().each({ Node child ->
            switch (child.name()) {
                case "build-flow":
                    prod.buildFlow = parse(child)
                    break
                case "inc-build-flow":
                    prod.incBuildFlow = parse(child)
                    break
                case "build-env":
                    prod.buildEnv = parse(child)
                    break
                case "build-node":
                    prod.buildNodes += parse(child)
                    break
                case "build-timeout":
                    prod.buildTimeout = parse(child)
                    break
                case "log-parsing":
                    prod.logParsing = parse(child)
                    break
                case "make-prefix":
                    prod.makePrefix = parse(child)
                    break
                case "make-root":
                    prod.makeRoot = parse(child)
                    break
                case "make-target":
                    prod.makeTarget = parse(child)
                    break
                case "pm":
                    prod.pm = parse(child)
                    break
                case "retention-policy":
                    prod.retentionPolicy = parse(child)
                    break
                case "techlead":
                    prod.techLead = parse(child)
                    break
                case "watcher":
                    prod.watchers += parse(child)
                    break
                case "sw-upgrade":
                    prod.swUpgrades += parse(child)
                    break
                case "unit-test":
                    prod.unitTest = parse(child)
                    break
                case "coverity":
                    prod.coverity = parse(child)
                    break
                case "csv-data-plot":
                    csvDataPlots += parse(child)
                    break
                case "doc":
                    prod.doc = parse(child)
                    break
                case "publish-build-over-ssh":
                case "publish-over-ssh":
                    prod.publishOverSSHList += parse(child)
                    break
                case "resources":
                    prod.resources = parse(child)
                    break
                case "variable":
                    prod.variables += parse(child)
                    break
                case "description":
                    prod.description = parse(child)
                    break
                case "incremental":
                    prod.incremental = parse(child)
                    break
                case "cache":
                    prod.cache = parse(child)
                    break
                case "credential":
                    prod.credentials += parse(child)
                    break
                case "custom-build-step":
                    prod.customBuildSteps.add(parse(child))
                    break
                case "debug":
                    prod.debug = parse(child)
                    break
                case "release":
                    prod.release = parse(child)
                    break
                case "production":
                    prod.production = parse(child)
                    break
                case "workspace-browsing":
                    prod.workspaceBrowsing = parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to product (child=${child.name()})")
                    break
            }
        })
        prod.csvDataPlots = csvDataPlots as CsvDataPlot[]
        return prod
    }

    protected Resources parseResources(Node node) {
        return new Resources(parseEnabledAttribute(node),
                node.attributes()['name'],
                node.attributes()['label'],
                node.attributes()['quantity'] as Integer
                )
    }

    /**
     * Returns null if not set, or set to "origin"
     * Otherwise true or false
     */
    protected Boolean parseRepositoryConfigurable(node) {
        String value = node.attributes()['configurable']
        if (value == null || value == "origin") {
            return null
        }
        return parseBooleanAttribute(node, 'configurable', false)
    }

    protected Repository parseRepository(Node node) {
        return new Repository(node.attributes()['name'],
                node.attributes()['dir'],
                node.attributes()['remote'],
                node.attributes()['branch'],
                parseRepositoryConfigurable(node))
    }


    protected RetentionPolicy parseRetentionPolicy(Node node) {
        RetentionPolicyType type
        switch (node.attribute('duration')) {
            case 'short':
                type = RetentionPolicyType.SHORT
                break
            case 'medium':
                type = RetentionPolicyType.MEDIUM
                break
            case 'long':
                type = RetentionPolicyType.LONG
                break
            case 'very-long':
                type = RetentionPolicyType.VERY_LONG
                break
            case 'infinite':
                type = RetentionPolicyType.INFINITE
                break
            default: throw new IllegalArgumentException("Invalid duration attribute (${node.attribute('duration')}) for retention-policy element.")
        }
        return RetentionPolicyFactory.create(type, parseBooleanAttribute(node, 'save-artifacts', true))
    }

    protected StartedBy parseStartedBy(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        return new StartedBy(enabled)
    }

    protected SwUpgrade parseSwUpgrade(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        int offset
        if (enabled) {
            offset = node.attributes()["offset"] as int
            if (offset <= 0) {
                throw new IllegalArgumentException("""The offset of <sw-upgrade offset="${
                    offset
                }"> must be a number larger than 0 (zero)""")
            }
        }
        return new SwUpgrade(offset, enabled)
    }

    protected Trigger parseTrigger(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        Boolean acceptNotifyCommit = parseBooleanAttribute(node, 'accept-notify-commit', false)
        return new Trigger(node.attributes()['polling'],
                node.attributes()['periodic'], acceptNotifyCommit, enabled)
    }

    protected PublishBuildOverSSH parsePublishBuildOverSSH(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        String name = node.attribute('name')
        String server = node.attribute('server')
        String artifactPattern = node.attribute('artifact-pattern')
        String removePrefix = node.attribute('remove-prefix')
        String rootDir = node.attribute('root-dir')
        Integer numberOfBuildsToKeep = node.attribute('number-of-builds-to-keep') as Integer
        String productAltName = node.attribute('product-alt-name')
        Integer retryTimes = node.attribute('retry-times') as Integer
        Integer retryDelay = node.attribute('retry-delay-ms') as Integer
        String label = node.attribute('label')

        return new PublishBuildOverSSH(enabled, name, server,
                artifactPattern, removePrefix, rootDir, numberOfBuildsToKeep, productAltName,
                retryTimes, retryDelay, label)
    }

    protected PublishOverSSH parsePublishOverSSH(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        String server = node.attribute('server')
        Integer retryTimes = node.attribute('retry-times') as Integer
        Integer retryDelay = node.attribute('retry-delay-ms') as Integer
        String label = node.attribute('label')
        List<TransferSet> transferSets = new ArrayList<TransferSet>()
        VariableCollection variables = new VariableCollection()

        node.children().each({ Node child ->
            switch (child.name()) {
                case "transfer-set":
                    transferSets.add(parseTransferSet(child))
                    break
                case "variable":
                    variables += parse(child)
                    break
                default:
                    throw new ConfigError("Unexpect child node to publish-over-ssh (child=${child.name()})")
            }
        })

        return new PublishOverSSH(enabled, server, retryTimes,
                retryDelay, label, transferSets).with {
                    it.variables = variables
                    it
                }
    }

    protected PublishTestReportOverSSH parsePublishTestReportOverSSH(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        String name = node.attribute('name')
        String server = node.attribute('server')
        String reportFilePattern = node.attribute('report-file-pattern')
        String removePrefix = node.attribute('remove-prefix')
        String suiteName = node.attribute('suite-name')
        Integer retryTimes = node.attribute('retry-times') as Integer
        Integer retryDelay = node.attribute('retry-delay-ms') as Integer
        String label = node.attribute('label')
        List<TransferSet> transferSets = new ArrayList<TransferSet>()
        VariableCollection variables = new VariableCollection()

        return new PublishTestReportOverSSH(enabled, name, server,
                reportFilePattern, removePrefix, suiteName,
                retryTimes, retryDelay, label)
    }

    protected TransferSet parseTransferSet(Node node) {
        String src = node.attribute('src')
        String removePrefix = node.attribute('remove-prefix')
        String remoteDir = node.attribute('remote-dir')
        String excludeFiles = node.attribute('exclude-files')
        String patternSeparator = node.attribute('pattern-separator')
        Boolean noDefaultExcludes = parseBooleanAttribute(node, 'no-default-excludes', null)
        Boolean makeEmptyDirs = parseBooleanAttribute(node, 'make-empty-dirs', null)
        Boolean flattenFiles = parseBooleanAttribute(node, 'flatten-files', null)
        Boolean remoteDirIsDateFormat = parseBooleanAttribute(node, 'remote-dir-is-date-format', null)
        Integer execTimeout = node.attribute('exec-timeout-ms') as Integer
        Boolean execInPTTY = parseBooleanAttribute(node, 'exec-in-pseudo-tty', null)
        String command = parseText(node)

        return new TransferSet(src, remoteDir, removePrefix, excludeFiles, patternSeparator, noDefaultExcludes,
                makeEmptyDirs, flattenFiles, remoteDirIsDateFormat, execTimeout, execInPTTY, command)
    }

    protected parseVariable(Node node) {
        return new Variable(node.attribute('name'), this.parseText(node))
    }

    protected ReleasePackaging parseReleasePackaging(Node node) {
        CustomBuildStepList cbss = new CustomBuildStepList()
        String stream = node.attribute('stream')
        Boolean configurable = parseBooleanAttribute(node, 'configurable', true)
        Boolean enabled = parseEnabledAttribute(node)
        PublishOverSSHList publishOverSSHList = []
        BuildTimeout buildTimeout = null
        Description description = null
        LogParsing logParsing = null
        CredentialList credentials = new CredentialList()
        Resources resources = null
        List<Repository> repositories = new ArrayList<Repository>()
        VariableCollection variables = new VariableCollection()

        node.children().each({ Node child ->
            switch (child.name()) {
                case "build-timeout":
                    buildTimeout = parse(child)
                    break
                case "credential":
                    credentials += parse(child)
                    break
                case "custom-build-step":
                    cbss.add(parse(child))
                    break
                case "publish-over-ssh":
                    publishOverSSHList += parse(child)
                    break
                case "description":
                    description = parse(child)
                    break
                case "log-parsing":
                    logParsing = parse(child)
                    break
                case "resources":
                    resources = parse(child)
                    break
                case "repository":
                    repositories.add(parse(child))
                    break
                case "variable":
                    variables += parse(child)
                    break
                default:
                    throw new ConfigError("Unexpected child node to release-packaging (child=${child.name()})")
            }
        })
        ReleasePackaging rp = new ReleasePackaging(configurable, enabled)
        rp.customBuildSteps = cbss
        rp.publishOverSSHList = publishOverSSHList
        rp.buildTimeout = buildTimeout
        rp.description = description
        rp.logParsing = logParsing
        rp.credentials = credentials
        rp.resources = resources
        rp.repositories = repositories as Repository[]
        rp.variables = variables
        return rp
    }

    protected Cache parseCache(Node node) {
        Boolean ccacheEnabled = parseBooleanAttribute(node, 'ccache-enabled', true)
        Boolean mcacheEnabled = parseBooleanAttribute(node, 'mcache-enabled', true)
        Boolean ccachePublish = parseBooleanAttribute(node, 'ccache-publish', true)
        Boolean mcachePublish = parseBooleanAttribute(node, 'mcache-publish', true)
        CcacheSize ccacheSize = CcacheSize.getFromString(node.attribute('ccache-size'))
        String ccacheStorage = node.attribute('ccache-storage')
        return new Cache(ccacheEnabled, ccachePublish, ccacheSize, ccacheStorage, mcacheEnabled, mcachePublish)
    }

    protected ConcurrentBuilds parseConcurrentBuilds(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        return new ConcurrentBuilds(enabled)
    }

    protected Credential parseCredential(Node node) {
        String id = node.attribute('id')
        String variableName = node.attribute('variable-name')
        Boolean enabled = parseEnabledAttribute(node)
        CredentialType type = null

        switch (node.attribute('type')) {
            case "text":
                type = CredentialType.TEXT
                break
            case "file":
                type = CredentialType.FILE
                break
            case "username-password":
                type = CredentialType.USERNAME_PASSWORD
                break
        }

        return new Credential(type, id, variableName, enabled)
    }

    protected WorkspaceBrowsing parseWorkspaceBrowsing(Node node) {
        Boolean enabled = parseEnabledAttribute(node)
        WorkspaceBrowsing workspacebrowsing = new WorkspaceBrowsing(enabled)
        return workspacebrowsing
    }

    protected Priority parsePriority(Node node) {
        Priority priority = Priority.getFromString(node.attribute('level'))
        return priority
    }
}
