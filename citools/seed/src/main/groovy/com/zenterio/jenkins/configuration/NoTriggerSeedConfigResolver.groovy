package com.zenterio.jenkins.configuration

class NoTriggerSeedConfigResolver implements IConfigResolver {

    /**
     * Internal Resolver that this wraps.
     */
    private IConfigResolver resolver

    /**
     *
     * @param resolver
     */
    public NoTriggerSeedConfigResolver(IConfigResolver resolver) {
        this.resolver = resolver
    }

    @Override
    public void resolve(Project[] projects) {
        this.resolver.resolve(projects)
        this.noPolling(projects)
    }

    /**
     * Overwrites all polling attributes to empty string
     * @param projects
     */
    private void noPolling(Project[] projects) {
        Trigger noTrigger = new Trigger(null, "", true)
        projects.each { Project project ->
             project.trigger = noTrigger.clone()
             project.incTrigger = noTrigger.clone()
             project.origins.each { Origin origin ->
                 origin.trigger = noTrigger.clone()
                 origin.incTrigger = noTrigger.clone()
                 origin.products.each { Product product ->
                     [product.debug,
                      product.release,
                      product.production].each { ProductVariant prodVariant ->
                          prodVariant.testGroups.each { TestGroup testGroup ->
                              testGroup.testContexts.each { TestContext testContext ->
                                  testContext.periodic = ""
                                  testContext.polling = null
                              }
                          }
                      }
                 }
             }
        }
    }
}
