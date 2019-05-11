
import com.zenterio.jenkins.application.CompilationRepositoryListFileApplication

def configDirPath = args[0]
def compilationRepoListFilePath = args[1]
def testRepoListFilePath = args[2]

CompilationRepositoryListFileApplication.generate(configDirPath,
                                                  compilationRepoListFilePath,
                                                  testRepoListFilePath)
