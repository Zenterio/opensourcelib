package com.zenterio.jenkins.configuration


class SeedConfigResolverMakeModsTest extends GroovyTestCase {

    SeedConfigResolver resolver
    Project proj
    def mods = [ makePrefix: new MakePrefix("test prefix value"),
        makeRoot: new MakeRoot( "test root name"),
        makeTarget: new MakeTarget("test target Name")]

    @Override
    protected void setUp() {
        this.resolver = new SeedConfigResolver()
        this.proj = Project.testData
    }

    protected void setModsNull(BaseConfig o) {
        mods.each { property, value ->
            o."$property" = null
        }
    }

    protected void setMods(BaseConfig o) {
        mods.each { property, value ->
            o."$property" = value
        }
    }

    protected void checkModsEquality(BaseConfig first, second) {
        mods.each { property, value ->
            assert first."$property" == second."$property"
        }
    }

    /**
     * All make mods (prefix, root, target) should be inherited as:
     * project -> origin -> product -> [debug, release, production]
     */
    public void testMakeModsAreInheritedFromProjectToProductVariant() {
        setMods(this.proj)

        Origin origin = proj.origins[0]
        Product prod = origin.products[0]
        ProductVariant d = prod.debug
        ProductVariant r = prod.release
        ProductVariant p = prod.production
        def all = [origin, prod, d, r, p]
        all.each { setModsNull(it) }

        this.resolver.resolve([this.proj] as Project[])
        all.each { checkModsEquality(this.proj, it) }
    }

    public void testDocInheritsmakePrefixFromProduct() {
        Product prod = proj.origins[0].products[0]
        setMods(prod)
        setModsNull(prod.doc)
        this.resolver.resolve([this.proj] as Project[])
        assert prod.makePrefix == prod.doc.makePrefix
    }

    public void testDocInheritsmakeRootFromProduct() {
        Product prod = proj.origins[0].products[0]
        setMods(prod)
        setModsNull(prod.doc)
        this.resolver.resolve([this.proj] as Project[])
        assert prod.makeRoot == prod.doc.makeRoot
    }

    public void testDocDoesNotInheritmakeTargetFromProduct() {
        Product prod = proj.origins[0].products[0]
        setMods(prod)
        setModsNull(prod.doc)
        this.resolver.resolve([this.proj] as Project[])
        assert prod.makeTarget != prod.doc.makeTarget
    }

    public void testDefaultValues() {
        Origin origin = proj.origins[0]
        Product prod = origin.products[0]
        ProductVariant d = prod.debug
        ProductVariant r = prod.release
        ProductVariant p = prod.production
        Doc doc = prod.doc
        def allCompile = [origin, prod, d, r, p]
        def all = [allCompile, doc].flatten()
        all.each { setModsNull(it) }
        this.resolver.resolve([this.proj] as Project[])
        all.each { BaseConfig o ->
            o.makePrefix = this.resolver.DEFAULT_MAKE_PREFIX
            o.makeRoot = this.resolver.DEFAULT_MAKE_ROOT
        }
        allCompile.each { BaseConfig o ->
            o.makeTarget = this.resolver.DEFAULT_COMPILATION_MAKE_TARGET
        }
        assert doc.makeTarget == this.resolver.DEFAULT_DOC_MAKE_TARGET
    }

}
