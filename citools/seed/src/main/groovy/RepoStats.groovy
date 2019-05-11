import static com.zenterio.jenkins.configuration.FilterProjects.filterProjects

import com.zenterio.jenkins.configuration.SeedConfigMerger
import com.zenterio.jenkins.configuration.SeedConfigResolver
import com.zenterio.jenkins.configuration.xml.ConfigXmlParser
import com.zenterio.jenkins.configuration.xml.ConfigXmlReader

def reader = new ConfigXmlReader(new ConfigXmlParser())
def merger = new SeedConfigMerger()
def resolver = new SeedConfigResolver()

def seedProjectFilter = System.getenv("ZENTERIO_SEED_PROJECT_FILTER")?.tokenize(' ')
def configFileFilter = System.getenv("ZENTERIO_SEED_CONFIG_FILE_FILTER")?.tokenize(' ')

def projects = filterProjects(reader.readDirectory("config", configFileFilter), seedProjectFilter)
projects = merger.merge(projects)
resolver.resolve(projects)

def collectRepoStats(projects) {
    def data = [:]

    for (project in projects) {
        for (origin in project.origins) {
            for (repository in origin.repositories) {
                if (!data.containsKey(repository.name)) {
                    data[repository.name] = [:]
                }
                if (!data[repository.name].containsKey(repository.branch)) {
                    data[repository.name][repository.branch] = 0
                }
                data[repository.name][repository.branch] += 1
            }
        }
    }
    return data
}

def printStats(stats) {
    for (repo in stats.keySet().toSorted()) {
        println("${repo}:")
        for (branch in stats[repo].keySet().toSorted()) {
            println("    ${branch}: ${stats[repo][branch]}")
        }
    }
}

def stats = collectRepoStats(projects)
printStats(stats)
