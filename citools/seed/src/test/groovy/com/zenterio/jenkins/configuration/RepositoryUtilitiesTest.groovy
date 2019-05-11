package com.zenterio.jenkins.configuration

class RepositoryUtilitiesTest extends GroovyTestCase
{
    void testGetSingleTestRespositoryFromTestGroupWithUpstreamTestContext() {
        def testGroup = TestGroup.testData
        def testRepositories = RepositoryUtilities.testRepositories(testGroup)

        assert testRepositories[0].testGroupName == "GROUP-NAME"
        assert testRepositories[0].repository.name == "REPOSITORY-NAME"
    }

    void testGetSingleTestRespositoryFromTestGroupWithAsyncUpstreamTestContext() {
        def testGroup = TestGroup.testData
        testGroup.testContexts[0].upstream = Upstream.ASYNC
        def testRepositories = RepositoryUtilities.testRepositories(testGroup)

        assert testRepositories[0].testGroupName == "GROUP-NAME"
        assert testRepositories[0].repository.name == "REPOSITORY-NAME"
    }

    void testGetSingleRespositoriesFromTestGroupWithNoUpstreamTestContext() {
        def testGroup = TestGroup.testData
        testGroup.testContexts[0].upstream = Upstream.FALSE
        def testRepositories = RepositoryUtilities.testRepositories(testGroup)

        assert testRepositories.length == 0
    }

    void testGetMultipleRespositoriesFromTestGroupWithUpstreamTestContext() {
        def testGroup = TestGroup.testData
        testGroup.repositories = [
                new Repository("name1", "dir1", "remote1", "branch1", false),
                new Repository("name2", "dir2", "remote2", "branch2", false),
        ]
        def testRepositories = RepositoryUtilities.testRepositories(testGroup)

        assert testRepositories[0].testGroupName == "GROUP-NAME"
        assert testRepositories[0].repository.name == "name1"
        assert testRepositories[1].testGroupName == "GROUP-NAME"
        assert testRepositories[1].repository.name == "name2"
    }

    void testRespositoriesFromTestGroupWithMultipleTestContexts() {
        def testGroup = TestGroup.testData
        testGroup.testContexts = [
                TestContext.testData,
                TestContext.testData,
        ]
        testGroup.testContexts[1].upstream = Upstream.FALSE
        def testRepositories = RepositoryUtilities.testRepositories(testGroup)

        assert testRepositories.length == 1
    }

    void testGetRepositoriesForProductVariantWithSingleTestGroup() {
        def productVariant = ProductVariant.testData
        def testRepositories = RepositoryUtilities.testRepositories(productVariant, false)
        assert testRepositories.length == 1
    }

    void testGetRepositoriesForProductWithSingleTestGroup() {
        def product = Product.testData
        def testRepositories = RepositoryUtilities.testRepositories(product, false)
        assert testRepositories.length == 1
    }

    void testGetRepositoriesForOriginWithSingleTestGroup() {
        def origin = Origin.testData
        def testRepositories = RepositoryUtilities.testRepositories(origin, false)
        assert testRepositories.length == 1
    }

    void testMergeSameRepositoriesForProductVariantForMultipleTestGroups() {
        def productVariant = ProductVariant.testData
        productVariant.testGroups = [TestGroup.testData, TestGroup.testData, TestGroup.testData]
        productVariant.testGroups.toList().withIndex().each({testGroup, index ->
            testGroup.name = "group${index+1}"
        })

        def testRepositories = RepositoryUtilities.testRepositories(productVariant, false)
        assert testRepositories.length == 3
        assert testRepositories[0].testGroupName == "group1"
        assert testRepositories[0].repository.name == "REPOSITORY-NAME"
        assert testRepositories[1].testGroupName == "group2"
        assert testRepositories[1].repository.name == "REPOSITORY-NAME"
        assert testRepositories[2].testGroupName == "group3"
        assert testRepositories[2].repository.name == "REPOSITORY-NAME"
    }

    void testMergeDifferentRepositoriesForProductVariantForMultipleTestGroups() {
        def productVariant = ProductVariant.testData
        productVariant.testGroups = [TestGroup.testData, TestGroup.testData, TestGroup.testData]
        productVariant.testGroups.toList().withIndex().each({TestGroup testGroup, index ->
            testGroup.name = "group${index+1}"
            testGroup.repositories[0].name = "repo${index+1}"
        })

        def testRepositories = RepositoryUtilities.testRepositories(productVariant, false)
        assert testRepositories.length == 3
        assert testRepositories[0].testGroupName == "group1"
        assert testRepositories[0].repository.name == "repo1"
        assert testRepositories[1].testGroupName == "group2"
        assert testRepositories[1].repository.name == "repo2"
        assert testRepositories[2].testGroupName == "group3"
        assert testRepositories[2].repository.name == "repo3"
    }

    void testMergeSameRepositoriesForProductsWithMultipleTestGroupsWithSameName() {
        def product = Product.testData
        product.debug = ProductVariant.testData
        product.production = ProductVariant.testData
        product.release = ProductVariant.testData

        def testRepositories = RepositoryUtilities.testRepositories(product, false)
        assert testRepositories.length == 1
    }

    void testMergeSameRepositoryInTestGroupsWithSameNameFailsWhenBranchIsDifferent() {
        def productVariant = ProductVariant.testData
        productVariant.testGroups = [TestGroup.testData, TestGroup.testData]
        productVariant.testGroups[0].repositories[0].branch = "some other branch"
        shouldFail(Exception) {
            RepositoryUtilities.testRepositories(productVariant, false)
        }
    }

    void testMergeSameRepositoryInTestGroupsWithSameNameFailsWhenRemoteIsDifferent() {
        def productVariant = ProductVariant.testData
        productVariant.testGroups = [TestGroup.testData, TestGroup.testData]
        productVariant.testGroups[0].repositories[0].remote = "some other remote"
        shouldFail(Exception) {
            RepositoryUtilities.testRepositories(productVariant, false)
        }
    }

    void testGetRepositoriesForIncrementalForProductVariant() {
        def productVariant = ProductVariant.testData
        def repository = Repository.testData
        repository.name = "inc-repo"
        def testGroup = TestGroup.testData
        testGroup.repositories = [repository]
        productVariant.incremental.testGroups = [testGroup]

        def testRepositories = RepositoryUtilities.testRepositories(productVariant, true)
        assert testRepositories.length == 1
        assert testRepositories[0].repository.name == "inc-repo"
    }

    void testModifiedTestRepositoriesClonesBeforeModifying() {
        def productVariant = ProductVariant.testData

        def testRepositories = RepositoryUtilities.modifiedTestRepositories(productVariant)
        assert productVariant.testGroups[0].repositories[0].envName == "REPOSITORY_NAME"
        assert productVariant.testGroups[0].repositories[0].directory == "DIRECTORY"
        assert productVariant.testGroups[0].repositories[0].allowTags

        assert testRepositories[0].envName == "REPOSITORY_NAME_GROUP_NAME"
        assert testRepositories[0].directory == "group_name/DIRECTORY"
        assert !testRepositories[0].allowTags
    }

    void testAllFlowRepositories() {
        def product = Product.testData
        product.repositories = [new Repository("build-repo", "dir", "build-remote", "branch", false)]

        def flowRepositories = RepositoryUtilities.allFlowRepositories(product)
        assert flowRepositories.length == 2
        assert flowRepositories[0].envName == "BUILD_REPO"
        assert flowRepositories[1].envName == "REPOSITORY_NAME_GROUP_NAME"
    }
}
