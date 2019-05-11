import com.zenterio.jenkins.configuration.xml.ConfigXmlParser
import com.zenterio.jenkins.configuration.xml.ConfigXmlReader
import com.zenterio.jenkins.configuration.SeedConfigMerger
import com.zenterio.jenkins.configuration.SeedConfigResolver
import com.zenterio.jenkins.configuration.BaseConfig
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.Product
import com.zenterio.jenkins.configuration.ProductVariant
import static com.zenterio.jenkins.configuration.FilterProjects.filterProjects
import com.zenterio.JSTreeJson

def reader = new ConfigXmlReader(new ConfigXmlParser())
def merger = new SeedConfigMerger()
def resolver = new SeedConfigResolver()
def seedProjectFilter = System.getenv("ZENTERIO_SEED_PROJECT_FILTER")?.tokenize(' ')
def configFileFilter = System.getenv("ZENTERIO_SEED_CONFIG_FILE_FILTER")?.tokenize(' ')

def renderer = new JSTreeJson<BaseConfig>(BaseConfig.class)

def configDirPath = args[0]
def outputFile = args[1]

def projects = filterProjects(reader.readDirectory(configDirPath, configFileFilter),
                              seedProjectFilter)
projects = merger.merge(projects)
resolver.resolve(projects)

renderer.toJsonFile(outputFile, projects)
