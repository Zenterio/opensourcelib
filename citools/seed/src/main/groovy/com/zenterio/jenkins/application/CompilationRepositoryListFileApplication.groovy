package com.zenterio.jenkins.application

import com.zenterio.jenkins.configuration.xml.ConfigXmlParser
import com.zenterio.jenkins.configuration.xml.ConfigXmlReader
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.configuration.SeedConfigMerger
import com.zenterio.jenkins.configuration.SeedConfigResolver
import com.zenterio.jenkins.configuration.Product
import com.zenterio.jenkins.configuration.ProductVariant
import com.zenterio.jenkins.configuration.TestGroup
import com.zenterio.jenkins.configuration.TestContext
import static com.zenterio.jenkins.configuration.FilterProjects.filterProjects

class CompilationRepositoryListFileApplication {

    final static ConfigXmlReader reader = new ConfigXmlReader(new ConfigXmlParser())
    final static SeedConfigMerger merger = new SeedConfigMerger()
    final static SeedConfigResolver resolver = new SeedConfigResolver()

    public static void generate(String configDirPath,
                                String compilationRepoListFilePath,
                                String testRepoListFilePath,
                                List<String> configFileFilter = new ArrayList<String>(),
                                List<String> projectFilter = new ArrayList<String>()) {
        def compilationRepoListFile = new File(compilationRepoListFilePath)
        def testRepoListFile = new File(testRepoListFilePath)
        generate(configDirPath, compilationRepoListFile, testRepoListFile,
            configFileFilter, projectFilter)
    }

    public static void generate(String configDirPath,
                                File compilationRepoListFile,
                                File testRepoListFile,
                                List<String> configFileFilter = new ArrayList<String>(),
                                List<String> projectFilter = new ArrayList<String>()) {
        compilationRepoListFile.getParentFile().mkdirs()
        testRepoListFile.getParentFile().mkdirs()
        def projects = getProjects(configDirPath, configFileFilter, projectFilter)
        def compilationRepos = getCompilationRepositories(projects)
        def testRepos = getTestRepositories(projects)
        compilationRepos.addAll(testRepos)
        write(compilationRepoListFile, compilationRepos)
        write(testRepoListFile, testRepos)
    }

    protected static ArrayList<Project> getProjects(String configPath,
            List<String> configFileFilter ,List<String> projectFilter) {
        def projects = filterProjects(reader.readDirectory(configPath, configFileFilter), projectFilter)
        projects = merger.merge(projects)
        resolver.resolve(projects)
        return projects
    }

    protected static ArrayList<Repository> getCompilationRepositories(List<Project> projects) {
        def repositories = []
        projects.each { Project proj ->
            proj.origins.each { Origin origin ->
                 repositories.addAll(origin.repositories)
                 repositories.addAll(origin.releasePackaging.repositories)
            }
        }
        return repositories
    }

    protected static ArrayList<Repository> getTestRepositories(List<Project> projects) {
        def repositories = []
        projects.each { Project proj ->
            proj.origins.each { Origin origin ->
                origin.products.each { Product prod ->
                    [prod.debug, prod.release, prod.production].grep({it}).each { ProductVariant prodVar ->
                        [prodVar.testGroups, prodVar.incremental.testGroups].flatten().each { TestGroup testGroup ->
                            testGroup.testContexts.each { TestContext testContext ->
                                repositories.addAll(testContext.repositories)
                            }
                        }
                    }
                }
            }
        }
        return repositories
    }

    protected static void write(File outputFile, ArrayList<Repository> repositories) {
        def repoComparator = [
            equals: { Repository first, Repository second ->
                first.name == second.name && first.remote == second.remote
            },
            compare: { Repository first, Repository second ->
                first.name <=> second.name
            }
        ] as Comparator

        def repoSorter = { Repository first, Repository second ->
                first.name <=> second.name
        }

        outputFile.withWriter('utf-8') { writer ->
            repositories.unique(repoComparator).sort(repoSorter).each { Repository repo ->
                writeEntry(writer, repo)
            }
        }

    }

    protected static void writeEntry(writer, Repository repo) {
        String sep = ' '
        writer.write(repo.name)
        writer.write(sep)
        writer.write(repo.remote)
        writer.write(System.getProperty("line.separator"))
    }

}
