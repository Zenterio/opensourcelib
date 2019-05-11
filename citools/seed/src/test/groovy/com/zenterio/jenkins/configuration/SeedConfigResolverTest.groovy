package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.buildtype.BuildTypeDebug

class SeedConfigResolverTest extends GroovyTestCase {

    SeedConfigResolver resolver

    @Override
    protected void setUp() {
        this.resolver = new SeedConfigResolver()
    }

    /**
     * Special case, watchers from project should be
     * propagated to origin but not to products.
     */
    public void testProjectWatchersAreAddedToOrigins() {
        Project proj = Project.testData
        int nWatchers = proj.watchers.size()
        nWatchers += proj.origins[0].watchers.size()
        int prodWatchers = proj.origins[0].products[0].watchers.size()

        this.resolver.resolve([proj] as Project[])
        assert proj.origins[0].watchers.size() == nWatchers
        assert prodWatchers == proj.origins[0].products[0].watchers.size()
    }

    /**
     * SetIfNull is one of the central update functions.
     * Use XX as example of a property that is propagated to products
     * using the setIfNull() function. However, make sure that the values are
     * copied, not referenced.
     */
    public void testSetIfNull() {
        Project proj = Project.testData
        this.resolver.resolve([proj] as Project[])
    }

    /**
     * SetIfNull should use inherit() instead of clone() for attributes that are
     * derived from BaseConfig, except from project to origin.
     * The project manager is one item that have a custom inherit(), as it is
     * derived from ContactInformation.
     * We need to check on product level however, as inheriting from project to origin always is a clone().
     */

    public void testSetIfNullUseOfInherit() {
        Project proj = Project.testData
        assert proj.pm.emailPolicy.policies[EmailPolicyJobType.SLOW_FEEDBACK] == EmailPolicyWhen.FAILURE
        assert proj.pm.emailPolicy.policies[EmailPolicyJobType.UTILITY] == EmailPolicyWhen.SUCCESS
        assert proj.origins[0].pm == null
        assert proj.origins[0].products[0].pm == null

        this.resolver.resolve([proj] as Project[])
        assert proj.origins[0].products[0].pm.emailPolicy.policies[EmailPolicyJobType.UTILITY] == EmailPolicyWhen.SUCCESS
        assert proj.origins[0].products[0].pm.emailPolicy.policies[EmailPolicyJobType.SLOW_FEEDBACK] == EmailPolicyWhen.NEVER
    }

    /**
     * SetIfNull should not overwrite existing value
     */
    public void testSetIfNullExistingValue() {
        Project proj = Project.testData
        this.resolver.resolve([proj] as Project[])
    }

    /**
     * SetIfEmpty is one of the central update functions.
     * Use repositories as example of a list of properties that are
     * propagated to products. However, make sure that the values are copied,
     * not referenced.
     */
    public void testSetIfEmpty() {
        Project proj = Project.testData
        assert proj.origins[0].products[0].repositories.length == 0
        this.resolver.resolve([proj] as Project[])
        assert proj.origins[0].products[0].repositories == proj.origins[0].repositories
        assert !proj.origins[0].products[0].repositories.is(proj.origins[0].repositories)
        assert proj.origins[0].products[0].repositories.length != 0
    }

    /**
     * SetIfEmpty should not overwrite existing values
     */
    public void testSetIfEmptyExistingValue() {
        Project proj = Project.testData
        proj.origins[0].products[0].repositories = new Repository[1]
        assert proj.origins[0].products[0].repositories.length == 1
        this.resolver.resolve([proj] as Project[])
        assert proj.origins[0].products[0].repositories != proj.origins[0].repositories
    }

    /**
     * SetIfZeroStr should overwrite null and empty string with new value.
     */
    public void testSetIfZeroStr() {
    }

    /**
     * setIfZeroStr should not overwrite existing values that are not null
     * or empty string.
     */
    public void testSetIfZeroStrExistingValue() {

    }

    /**
     * setEmailPolicyIfNeeded will do some recursion if needed
     * Test using specially crafted Origin.
     */
    public void testSetEmailPolicyIfNeeded() {
        Origin origin = new Origin("TestingOrigin", false, true, null, null,
            [new Watcher("watcher","watcher@mail", null)] as ContactInformationCollection)
        origin.pm = ProjectManager.testData
        origin.techLead = new TechLead("TechleadOrigin", "techlead@origin", null)
        ProductVariant productVariant = new ProductVariant(new BuildTypeDebug(), true)
        productVariant.techLead = new TechLead("TechleadDebug", "techlead@debug", EmailPolicy.testData)
        origin.debug = productVariant

        assert origin.watchers[0].emailPolicy == null
        assert origin.pm.emailPolicy == EmailPolicy.testData
        assert origin.techLead.emailPolicy == null
        assert origin.debug.techLead.emailPolicy == EmailPolicy.testData

        SeedConfigResolver.setMissingEmailPolicy(origin)

        assert origin.watchers[0].emailPolicy == new EmailPolicy(EmailPolicyWhen.FAILURE,
                EmailPolicyWhen.NEVER, EmailPolicyWhen.NEVER, EmailPolicyWhen.NEVER)
        assert origin.pm.emailPolicy == EmailPolicy.testData
        assert origin.techLead.emailPolicy == new EmailPolicy(EmailPolicyWhen.FAILURE,
                EmailPolicyWhen.NEVER, EmailPolicyWhen.NEVER, EmailPolicyWhen.NEVER)
        assert origin.debug.techLead.emailPolicy == EmailPolicy.testData

    }

}
