
class Configuration{
    String name
    String dir
    String[] skipStages
    Boolean systestCoverage
    String znakePrefix
    String artifactoryUrl
}

def call(Map map = [:]){
    def defaults = [dir: null, skipStages: [], systestCoverage: true, znakePrefix: '', artifactoryUrl: 'https://linsartifact.zenterio.lan']
    def config = new Configuration(defaults << map)

    def znake = "${config.znakePrefix}znake -e --root"
    def workdir = config.dir?"\${WORKSPACE}/${config.dir}":"\${WORKSPACE}"
    def builddir = config.dir?"${config.dir}/build":'build'

    pipeline {
        agent {
            label 'build'
        }

        parameters {
            booleanParam(defaultValue: true, description: 'Publish artifacts', name: 'PUBLISH')
        }

        stages {
            stage('Setup') {
                when {
                    expression {return ! config.skipStages.contains('Setup')}
                }
                steps {
                    bash "git clean -fdx"
                    bash """cd "${workdir}" && source ./activate""", '-ex'
                }
            }
            stage('Package') {
                parallel {
                    stage('Static') {
                        when {
                            expression {return ! config.skipStages.contains('Static')}
                        }
                        steps {
                            bash """cd "${workdir}" && ${znake} static"""
                        }
                    }
                    stage('Test') {
                        when {
                            expression {return ! config.skipStages.contains('Test')}
                        }
                        steps {
                            bash """cd "${workdir}" && ${znake} --coverage test.all"""
                        }
                    }
                    stage('Systest') {
                        when {
                            expression {return ! config.skipStages.contains('Systest')}
                        }
                        steps {
                            bash """cd "${workdir}" && ${znake}${config.systestCoverage?' --coverage':''} systest"""
                        }
                        post {
                            always {
                                //step([$class: 'Publisher', reportFilenamePattern: "${builddir}/test/output-local/reports/testng/testng-results.xml"])
                                archiveArtifacts "${builddir}/test/output-local/logs/**"
                            }
                        }
                    }
                    stage('Pypi') {
                        when {
                            expression {return ! config.skipStages.contains('Pypi')}
                        }
                        steps {
                            bash """cd "${workdir}" && ${znake} pypi"""
                        }
                        post {
                            always {
                                archiveArtifacts "${builddir}/pypi/sdist/*.tar.gz"
                                archiveArtifacts "${builddir}/pypi/wheel/*.whl"
                            }
                        }
                    }
                    stage('-') {
                        stages {
                            stage('Doc') {
                                when {
                                    expression {return ! config.skipStages.contains('Doc')}
                                }
                                steps {
                                    bash """cd "${workdir}" && ${znake} doc"""
                                    bash """cd "${workdir}"/build/doc && tar cf - user_guide | gzip -9 > user_guide.tar.gz"""
                                }
                                post {
                                    always {
                                        archiveArtifacts "${builddir}/doc/user_guide.tar.gz"
                                    }
                                }
                            }
                            stage('Deb') {
                                when {
                                    expression {return ! config.skipStages.contains('Deb')}
                                }
                                steps {
                                    bash """cd "${workdir}" && ${znake} deb"""
                                }
                                post {
                                    always {
                                        archiveArtifacts "${builddir}/dist/*/*.deb"
                                    }
                                }
                            }
                            stage('Debtest') {
                                when {
                                    expression {return ! config.skipStages.contains('Debtest')}
                                }
                                steps {
                                    bash """cd "${workdir}" && ${znake} debtest"""
                                }
                                post {
                                    always {
                                        //step([$class: 'Publisher', reportFilenamePattern: "${builddir}/test/output-u*/reports/testng/testng-results.xml"])
                                        archiveArtifacts "${builddir}/test/output-u*/logs/**"
                                    }
                                }
                            }
                        }
                    }
                }
            }
            stage('Publish') {
                when {
                     expression {return params.PUBLISH && ! config.skipStages.contains('Publish')}
                }
                environment {
                    // ARTIFACTORY_CREDENTIALS is set to username:password and ARTIFACTORY_CREDENTIALS_USR and ARTIFACTORY_CREDENTIALS_PSW are created automatically
                    ARTIFACTORY_CREDENTIALS = credentials('artifactory-credentials')
                }
                parallel {
                    stage('Publish Doc') {
                        when {
                            expression {return ! config.skipStages.contains('Doc')}
                        }
                        steps {
                            bash """cd "${workdir}" && curl -v -X PUT -u "\${ARTIFACTORY_CREDENTIALS_USR}":"\${ARTIFACTORY_CREDENTIALS_PSW}" "${config.artifactoryUrl}/artifactory/docs/${config.name.capitalize()}/user_guide-${env.BUILD_NUMBER.toInteger() + 1000}.tar.gz" -T "${builddir}"/doc/user_guide.tar.gz"""
                        }
                    }
                    stage('Publish Deb') {
                        when {
                            expression {return ! config.skipStages.contains('Deb')}
                        }
                        steps {
                            sh """#!/bin/bash
                                set -eux
                                cd "${workdir}"
                                for dir in build/dist/*; do
                                    codename=\$(basename \${dir})
                                    debian_package_name=\$(basename \${dir}/*.deb)
                                    curl -v -X PUT -u"\${ARTIFACTORY_CREDENTIALS_USR}":"\${ARTIFACTORY_CREDENTIALS_PSW}" -XPUT "${config.artifactoryUrl}/artifactory/debian-local/pool/\${debian_package_name};deb.distribution=\${codename};deb.component=main;deb.architecture=amd64" -T \${dir}/*.deb
                                done
                            """
                        }
                    }
                    stage('Publish Pypi') {
                        when {
                            expression {return ! config.skipStages.contains('Pypi')}
                        }
                        steps {
                            bash """cd "${workdir}" && twine upload build/pypi/sdist/* build/pypi/wheel/* --repository-url http://pip.zenterio.lan/artifactory/api/pypi/pypi-local -u "${ARTIFACTORY_CREDENTIALS_USR}" -p "${ARTIFACTORY_CREDENTIALS_PSW}" """
                        }
                    }
                }
            }
        }
    }
}
