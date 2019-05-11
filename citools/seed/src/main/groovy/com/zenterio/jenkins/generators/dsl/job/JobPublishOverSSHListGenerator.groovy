package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.configuration.PublishOverSSH
import com.zenterio.jenkins.configuration.TransferSet
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobPublishOverSSHListModel
import javaposse.jobdsl.dsl.Job

class JobPublishOverSSHListGenerator implements IPropertyGenerator {

    @Override
    void generate(ModelProperty model, Object entity) {
        JobPublishOverSSHListModel m = (JobPublishOverSSHListModel) model
        Job job = (Job) entity
        if (m.publishOverSSHList.size() > 0) {
            job.with {
                publishers {
                    publishOverSsh {
                        m.publishOverSSHList.each { PublishOverSSH publishOverSSHModel ->
                            server(publishOverSSHModel.server) {
                                retry(publishOverSSHModel.retryTimes, publishOverSSHModel.retryDelay)
                                label(publishOverSSHModel.label)

                                assert publishOverSSHModel.transferSets.size() > 0
                                publishOverSSHModel.transferSets.each { TransferSet set ->
                                    transferSet {
                                        sourceFiles(set.src)
                                        execCommand(set.command)
                                        removePrefix(set.removePrefix)
                                        remoteDirectory(set.remoteDir)
                                        excludeFiles(set.excludeFiles)
                                        patternSeparator(set.patternSeparator)
                                        noDefaultExcludes(set.noDefaultExcludes)
                                        makeEmptyDirs(set.makeEmptyDirs)
                                        flattenFiles(set.flattenFiles)
                                        remoteDirIsDateFormat(set.remoteDirIsDateFormat)
                                        execTimeout(set.execTimeout)
                                        execInPty(set.execInPTTY)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
