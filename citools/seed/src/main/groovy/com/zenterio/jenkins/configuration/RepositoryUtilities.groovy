package com.zenterio.jenkins.configuration


public class RepositoryUtilities {

    /**
     * Generates an array of all repositories needed by a flow to generate parameters
     * and git handling. The test repositories are modified to not get collisions between
     * parameter names and directories.
     * @param config is the config object matching the flow
     * @param incremental tells if normal or incremental test groups should be checked for test repositories
     * @return array with all repositories
     */
    public static Repository[] allFlowRepositories(BaseCompilationStructureConfig config, Boolean incremental=false) {
        def allRepositories = []
        allRepositories.addAll(config.repositories)
        allRepositories.addAll(modifiedTestRepositories(config, incremental))
        return allRepositories as Repository[]
    }

    /**
     * Generates an array of test repositories. The repositories are modified to not
     * get collisions between parameter names and directories.
     * @param config is the config object to start looking for test repositories in
     * @param incremental tells if normal or incremental test groups should be checked for test repositories
     * @return array with test repositories
     */
    public static Repository[] modifiedTestRepositories(BaseCompilationStructureConfig config, Boolean incremental=false) {
        return testRepositories(config, incremental).collect({
            TestRepositoryInfo repoInfo ->
                repoInfo.modifiedRepository()
        })
    }

    public static TestRepositoryInfo[] testRepositories(Project project, Boolean incremental) {
        return internalTestRepositories(project.origins, incremental)
    }

    public static TestRepositoryInfo[] testRepositories(Origin origin, Boolean incremental) {
        return internalTestRepositories(origin.products, incremental)
    }

    public static TestRepositoryInfo[] testRepositories(Product product, Boolean incremental) {
        return internalTestRepositories([product.debug, product.production, product.release] as BaseConfig[], incremental)
    }

    public static TestRepositoryInfo[] testRepositories(ProductVariant productVariant, Boolean incremental) {
        if (incremental) {
            return internalTestRepositories(productVariant.incremental.testGroups, incremental)
        } else {
            return internalTestRepositories(productVariant.testGroups, incremental)
        }
    }

    public static TestRepositoryInfo[] testRepositories(TestGroup testGroup, Boolean incremental=false) {
        def allTestRepositories = []

        if (hasUpstreamTestContext(testGroup)) {
            for (repo in testGroup.repositories) {
                allTestRepositories.add(new TestRepositoryInfo(testGroup.name, repo))
            }
        }
        return allTestRepositories
    }

    private static Boolean hasUpstreamTestContext(TestGroup testGroup) {
        return testGroup.testContexts.toList().any({testContext ->
            testContext.upstream in [Upstream.TRUE, Upstream.ASYNC]})
    }

    private static TestRepositoryInfo[] internalTestRepositories(BaseConfig[] configs, Boolean incremental) {
        List<TestRepositoryInfo> allTestRepositories = new ArrayList<>()

        for (config in configs) {
            for (TestRepositoryInfo repoInfo in testRepositories(config, incremental)) {
                TestRepositoryInfo existingRepoInfo = allTestRepositories.find({existingRepoInfo ->
                    repoInfo.testGroupName == existingRepoInfo.testGroupName && repoInfo.repository.name == existingRepoInfo.repository.name
                })

                if (existingRepoInfo == null) {
                    allTestRepositories.add(repoInfo)
                } else if (existingRepoInfo.repository.remote != repoInfo.repository.remote) {
                    throw new Exception("All repositories for test groups with the same name need to use the same remote")
                } else if (existingRepoInfo.repository.branch != repoInfo.repository.branch) {
                    throw new Exception("All repositories for test groups with the same name need to use the same branch")
                }
            }
        }
        return allTestRepositories
    }
}
