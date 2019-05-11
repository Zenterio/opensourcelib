package com.zenterio.jenkins.configuration

/**
 * A configuration reader is the interface used to extract a configuration
 * from a file path.
 *
 */
interface IConfigReader {
    public Project[] readDirectory(String directoryPath, List<String> configFileFilter);
    public Project[] readFile(String filePath);
}
