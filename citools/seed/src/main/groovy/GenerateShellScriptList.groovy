
import com.zenterio.jenkins.application.XmlSeedShellscriptApplication

def app = new XmlSeedShellscriptApplication('scriptlets', args[1])

def seedConfigFilter = System.getenv("ZENTERIO_SEED_PROJECT_FILTER")?.tokenize(',')
def configFileFilter = System.getenv("ZENTERIO_SEED_CONFIG_FILE_FILTER")?.tokenize(' ')

app.seedDirectory(args[0], configFileFilter, seedConfigFilter)
