
import com.zenterio.jenkins.application.XmlSeedConsoleApplication

def app = new XmlSeedConsoleApplication("scriptlets")

def seedConfigFilter = System.getenv("ZENTERIO_SEED_PROJECT_FILTER")?.tokenize(',')
def configFileFilter = System.getenv("ZENTERIO_SEED_CONFIG_FILE_FILTER")?.tokenize(' ')

app.seedDirectory("config", configFileFilter ,seedConfigFilter)
app.seedDirectory("src/test/resources/config", configFileFilter, seedConfigFilter)
