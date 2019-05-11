package com.zenterio.jenkins.builders

import com.zenterio.jenkins.builders.JasmineCommandBuilder
import com.zenterio.jenkins.configuration.Jasmine
import com.zenterio.jenkins.configuration.Repository

class JasmineCommandBuilderTest extends GroovyTestCase {

    JasmineCommandBuilder builder

    protected Repository[] getRepositories() {
        return [new Repository('repo0', 'repo0', 'git@REMOTE:repo0', 'BRANCH', false),
            new Repository('repo1', 'repo1', 'git@REMOTE:repo1', 'BRANCH', false),
            new Repository('repo2', 'repo2', 'git@REMOTE:repo2', 'BRANCH', false),
            ] as Repository[]
    }

    @Override
    protected void setUp() throws Exception {
        super.setUp()
        builder = new JasmineCommandBuilder(new Jasmine('repo1', 'conf.json', null, true, true),
                getRepositories())
    }

    void testGetJasmineArgumentsAll() {
        assert builder.getJasmineArguments() == '--jasmine_config conf.json --disable_rcu --disable-check rcu'
    }

    void testGetJasmineArgumentsWithoutDisableRCU() {
        builder.jasmine.disableRCU = false
        assert builder.getJasmineArguments() == '--jasmine_config conf.json --disable-check rcu'
    }

    void testGetJasmineArgumentsWithoutDisableRCUCheck() {
        builder.jasmine.disableRCUCheck = false
        assert builder.getJasmineArguments() == '--jasmine_config conf.json --disable_rcu'
    }

    void testGetJasmineRepositoryPathNotAJasmineTest() {
        builder.jasmine = null
        assert builder.getJasmineRepositoryPath() == ''
    }

    void testGetJasmineRepositoryPathToExistingRepository() {
        assert builder.getJasmineRepositoryPath() == '${WORKSPACE}/repo1'
    }

    void testGetJasmineRepositoryPathToNoneExistingRepository() {
        builder.repositories = [builder.repositories[0]]
        shouldFail(IllegalStateException, {
            builder.getJasmineRepositoryPath() == '${WORKSPACE}/repo1'
        })
    }

    void testGetCommandNoJasmineTest() {
        builder.jasmine = null
        assert builder.getCommand() == ''
    }

    void testGetCommandJasmineTest() {
        assert builder.getCommand() ==
                '--config jasminebasepage=http://10.20.10.75/hydra/gitcc/repo1/' +
                '"$(cd "${WORKSPACE}/repo1" && git rev-parse HEAD)"/jasmineTests/AutoTest.html ' +
                '--jasmine_config conf.json --disable_rcu --disable-check rcu'
    }
    void testNotSetUrl() {
        builder = new JasmineCommandBuilder(new Jasmine('repo1', 'conf.json', null, true, true),
                getRepositories())
        assert builder.getCommand() ==
                '--config jasminebasepage=http://10.20.10.75/hydra/gitcc/repo1/' +
                '"$(cd "${WORKSPACE}/repo1" && git rev-parse HEAD)"/jasmineTests/AutoTest.html ' +
                '--jasmine_config conf.json --disable_rcu --disable-check rcu'
    }
    void testSetUrl() {
        builder = new JasmineCommandBuilder(new Jasmine('repo1', 'conf.json', 'http://linstest.zenterio.lan/jasmineTests/AutoTest.html', true, true),
                getRepositories())
        assert builder.getCommand() ==
                '--config jasminebasepage=http://linstest.zenterio.lan/jasmineTests/AutoTest.html ' +
                '--jasmine_config conf.json --disable_rcu --disable-check rcu'
    }

}
