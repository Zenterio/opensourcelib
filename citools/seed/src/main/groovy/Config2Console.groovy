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
println(projects)

projects = filterProjects(reader.readDirectory("src/test/resources/config", configFileFilter),
    seedProjectFilter)
projects = merger.merge(projects)
resolver.resolve(projects)
println(projects)
