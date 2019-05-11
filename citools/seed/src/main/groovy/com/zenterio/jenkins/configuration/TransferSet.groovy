package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@AutoClone
@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class TransferSet extends BaseConfig{

    /**
     * Files to upload to a server.
     */
    String src;

    /**
     * First part of the file path that should not be created on the remote server.
     */
    String removePrefix;

    /**
     * Optional destination folder.
     */
    String remoteDir;

    /**
     * Files to be excluded when copying.
     */
    String excludeFiles;

    /**
     * The regular expression that is used to separate the Source files and Exclude files patterns.
     */
    String patternSeparator;

    /**
     * Disable the default exclude patterns.
     */
    Boolean noDefaultExcludes;

    /**
     * Create any directories that match the Source files pattern, even if empty.
     */
    Boolean makeEmptyDirs;

    /**
     * Only create files on the server, don't create directories (except for the remote directory, if present).
     */
    Boolean flattenFiles;

    /**
     * Select this to indicate that some part of the remote directory should be interpreted as a timestamp pattern.
     */
    Boolean remoteDirIsDateFormat;

    /**
     * Timeout in milliseconds for the Exec command.
     * Set to zero to disable.
     */
    int execTimeout;

    /**
     * Exec the command in a pseudo tty
     * This will enable the execution of sudo commands that require a tty (and possibly help in other scenarios too.)
     */
    Boolean execInPTTY;

    /**
     * The command to execute after potential file transferees have been completed.
     */
    String command;

    public TransferSet(String src,
                       String remoteDir,
                       String removePrefix,
                       String excludeFiles,
                       String patternSeparator,
                       Boolean noDefaultExcludes,
                       Boolean makeEmptyDirs,
                       Boolean flattenFiles,
                       Boolean remoteDirIsDateFormat,
                       Integer execTimeout,
                       Boolean execInPTTY,
                       String command) {

        if (!src && !command)
            throw new IllegalArgumentException('At least one of the src and command parameter has to be present in a transfer set.')

        this.src = src ?: ""
        this.remoteDir = remoteDir ?: ""
        this.removePrefix = removePrefix ?: ""
        this.excludeFiles = excludeFiles ?: ""
        this.patternSeparator = patternSeparator ?: "[, ]+"
        this.noDefaultExcludes = noDefaultExcludes ?: false
        this.makeEmptyDirs = makeEmptyDirs ?: false
        this.flattenFiles = flattenFiles ?: false
        this.remoteDirIsDateFormat = remoteDirIsDateFormat ?: false
        this.execTimeout = execTimeout ?: 120000
        this.execInPTTY = execInPTTY ?: false
        this.command = command ?: ""
    }
}
