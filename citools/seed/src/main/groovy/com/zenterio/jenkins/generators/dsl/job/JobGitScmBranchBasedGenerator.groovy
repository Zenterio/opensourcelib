package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobGitScmBranchBasedModel
import com.zenterio.jenkins.models.job.RepositoryConfigurable

class JobGitScmBranchBasedGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        JobGitScmBranchBasedModel m = (JobGitScmBranchBasedModel) model
        if (m.repositories.length > 0) {
            entity.with {
                multiscm {
                    m.repositories.each { Repository repo ->
                        Boolean useRefSpec = !getConfigurable(repo, m)
                        git {
                            remote {
                                name repo.name
                                url repo.remote
                                if (useRefSpec) {
                                    refspec "+refs/heads/${repo.branch}:refs/remotes/${repo.name}/${repo.branch}"
                                }
                            }
                            branch getRevision(repo, m.useParameters)
                            extensions {
                                cloneOptions {
                                    timeout(20)
                                    reference("\${BUILD_SERVER_GIT_CACHE}/${repo.name}.git")
                                    if (useRefSpec) {
                                        honorRefspec(true)
                                    }
                                    noTags(false)
                                }
                                relativeTargetDirectory repo.directory
                                if (m.getCreateBuildTag() && repo.allowTags) {
                                    perBuildTag()
                                }
                                submoduleOptions {
                                    recursive()
                                }
                                if (! m.acceptNotifyCommit || ! repo.allowNotifyCommit) {
                                    ignoreNotifyCommit()
                                }
                            }
                            if (!repo.allowNotifyCommit) {
                                configure { gitcontext ->
                                    gitcontext / 'extensions' / 'hudson.plugins.git.extensions.impl.PollExclusion'

                                }
                            }
                        }
                    }
                }
            }
        }
    }

    protected String getRevision(Repository repo, Boolean useParameters) {
        return (useParameters) ? "\${${repo.envName}}" : repo.branch
    }

    protected Boolean getConfigurable(Repository repo, JobGitScmBranchBasedModel m) {
        Boolean result = null
        switch (m.repoConfigurable) {
            case RepositoryConfigurable.OPTIONAL:
                result = repo.configurable
                break;
            case RepositoryConfigurable.FORCE_TRUE:
                result = true
                break;
            case RepositoryConfigurable.FORCE_FALSE:
                result = false
                break;
            default:
                throw Exception("RepositoryConfigurable value ${m.repoConfigurable} not supported.")

        }
        return result
    }

}
