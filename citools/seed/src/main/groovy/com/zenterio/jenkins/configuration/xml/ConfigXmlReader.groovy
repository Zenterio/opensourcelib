package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.IConfigReader

import groovy.io.FileType

import groovy.util.logging.*

@Log
class ConfigXmlReader implements IConfigReader {

    private ConfigXmlParser parser

    public ConfigXmlReader(ConfigXmlParser parser) {
        this.parser = parser
    }

    @Override
    public Project[] readDirectory(String directoryPath, List<String> configFileFilter) {
        def projects = []
        def files = collectFiles(directoryPath, configFileFilter)

        files.sort({ a, b -> a.toLowerCase() <=> b.toLowerCase() }).each { String filePath ->
            projects += readFile(filePath).toList()
        }

        return projects as Project[]
    }

    private List<String> collectFiles(String directoryPath, List<String> configFileFilter) {
        def files = []
        def confDir = new File(directoryPath)

        confDir.eachFile(FileType.FILES) { confFile ->
            if(confFile.name.endsWith('.xml')) {
                if (!configFileFilter || (confFile.name in configFileFilter)) {
                    files += confFile.absolutePath
                }
            }
        }

        confDir.eachDir { subConfDir ->
            subConfDir.eachFile(FileType.FILES) { confFile ->
                if(confFile.name.endsWith('.xml')) {
                    if (!configFileFilter || (subConfDir.name in configFileFilter)) {
                        files += confFile.absolutePath
                    }
                }
            }
        }
        return files as List<String>
    }

    @Override
    public Project[] readFile(String filePath) {
        return this.parser.parseFile(filePath)
    }
}
