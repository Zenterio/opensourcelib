package com.zenterio.jenkins.configuration


class SeedConfigResolverVariablesTest extends GroovyTestCase {

    SeedConfigResolver resolver
    Project proj

    @Override
    protected void setUp() {
        this.resolver = new SeedConfigResolver()
        this.proj = Project.testData
    }

    protected void clearVariables(IVariableContext cfg) {
        cfg.variables.clear()
    }

    protected void checkVariablesEquality(IVariableContext first,
            BaseConfig other) {
        assert first.variables == other.variables
    }

    protected void setVariables(IVariableContext cfg) {
        cfg.variables.add(new Variable("test-name", "test-value"))
    }

    /**
     * Variables should be inherited and merged:
     * project -> origin -> product -> [debug, release, production]
     */
    public void testVariablesAreInheritedFromProjectToProductVariant() {
        clearVariables(this.proj)
        setVariables(this.proj)

        Origin origin = proj.origins[0]
        Product prod = origin.products[0]
        ProductVariant d = prod.debug
        ProductVariant r = prod.release
        ProductVariant p = prod.production
        def all = [origin, prod, d, r, p]
        all.each { clearVariables(it) }

        this.resolver.resolve([this.proj] as Project[])
        all.each { checkVariablesEquality(this.proj, it) }
    }

    public void testVariablesAreMerged() {
        Origin origin = proj.origins[0]
        Product prod = origin.products[0]
        ProductVariant d = prod.debug
        clearVariables(this.proj)
        clearVariables(origin)
        clearVariables(prod)
        clearVariables(d)
        this.proj.variables.add(new Variable("var1", "proj"))
        origin.variables.add(new Variable("var2", "origin"))
        prod.variables.add(new Variable("var3", "product"))
        d.variables.add(new Variable("var4", "debug"))

        this.resolver.resolve([this.proj] as Project[])

        assert d.variables.getValue("var1") == "proj"
        assert d.variables.getValue("var2") == "origin"
        assert d.variables.getValue("var3") == "product"
        assert d.variables.getValue("var4") == "debug"
    }

    public void testDocInheritsFromProduct() {
        Product prod = proj.origins[0].products[0]
        Doc doc = prod.doc
        setVariables(prod)
        clearVariables(doc)
        this.resolver.resolve([this.proj] as Project[])
        checkVariablesEquality(prod, doc)
    }

    public void testCovInheritsFromProduct() {
        Product prod = proj.origins[0].products[0]
        Coverity cov = prod.coverity
        setVariables(prod)
        clearVariables(cov)
        this.resolver.resolve([this.proj] as Project[])
        checkVariablesEquality(prod, cov)
    }

    public void testTestGroupInheritsFromProductVariant() {
        ProductVariant d = proj.origins[0].products[0].debug
        TestGroup tg = d.testGroups[0]
        setVariables(d)
        clearVariables(tg)
        this.resolver.resolve([this.proj] as Project[])
        checkVariablesEquality(d, tg)
    }

    public void testTestContextInheritsFromTestGroup() {
        TestGroup tg = proj.origins[0].products[0].debug.testGroups[0]
        TestContext tc = tg.testContexts[0]
        setVariables(tg)
        clearVariables(tc)
        this.resolver.resolve([this.proj] as Project[])
        checkVariablesEquality(tg, tc)
    }

    public void testReleasePackagingInheritsFromOrigin() {
        Origin origin = proj.origins[0]
        ReleasePackaging pkg = origin.releasePackaging
        setVariables(origin)
        clearVariables(pkg)
        this.resolver.resolve([this.proj] as Project[])
        checkVariablesEquality(origin, pkg)
    }

    public void testPublishOverSSHInheritsFromParent() {
        ReleasePackaging pkg = proj.origins[0].releasePackaging
        Doc doc = proj.origins[0].products[0].doc
        Coverity cov = proj.origins[0].products[0].coverity
        ProductVariant d = proj.origins[0].products[0].debug
        ProductVariant r = proj.origins[0].products[0].release
        ProductVariant p = proj.origins[0].products[0].production
        TestContext tc = d.testGroups[0].testContexts[0]
        def all = [pkg, doc, cov, d, r, p, tc]
        all.each { it ->
            setVariables (it)
            clearVariables(it.publishOverSSHList[0])
        }
        this.resolver.resolve([this.proj] as Project[])
        all.each { it ->
            checkVariablesEquality(it, it.publishOverSSHList[0])
        }
    }

    public void testIncrementalDoesNotInheritsFromProductVariant() {
        ProductVariant d = proj.origins[0].products[0].debug
        Incremental inc = d.incremental
        setVariables(d)
        clearVariables(inc)
        this.resolver.resolve([this.proj] as Project[])
        assert d.variables != inc.variables
    }

    public void testTestGroupInheritsFromIncremental() {
        Incremental inc = proj.origins[0].products[0].debug.incremental
        TestGroup tg = inc.testGroups[0]
        setVariables(inc)
        clearVariables(tg)
        this.resolver.resolve([this.proj] as Project[])
        checkVariablesEquality(inc, tg)
    }

    public void testTestContextInheritsFromIncrementalTestGroup() {
        TestGroup tg = proj.origins[0].products[0].debug.incremental.testGroups[0]
        TestContext tc = tg.testContexts[0]
        setVariables(tg)
        clearVariables(tc)
        this.resolver.resolve([this.proj] as Project[])
        checkVariablesEquality(tg, tc)
    }

}
