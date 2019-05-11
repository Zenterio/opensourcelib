FROM jenkins/jenkins:lts

ENV JAVA_OPTS="-Djava.awt.headless=true -Djenkins.install.runSetupWizard=false"
ENV CASC_JENKINS_CONFIG="/var/jenkins_home/casc_configs"
ENV JENKINS_SSH_PRIVATE_KEY=""

RUN echo 2.0 > /usr/share/jenkins/ref/jenkins.install.UpgradeWizard.state

COPY official_plugins.txt /usr/share/jenkins/ref/official_plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/official_plugins.txt

COPY bundled_plugins /usr/share/jenkins/ref/plugins

COPY ssh /root/.ssh

USER root

RUN \
apt-get update && \
apt-get install --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" rsync

USER jenkins

RUN mkdir -p "${CASC_JENKINS_CONFIG}"