FROM jenkins/jenkins:lts

ENV JAVA_OPTS="-Djava.awt.headless=true -Djenkins.install.runSetupWizard=false -Djdk.tls.trustNameService=true -Dhudson.plugins.active_directory.ActiveDirectorySecurityRealm.forceLdaps=true"
ENV CASC_JENKINS_CONFIG="/var/jenkins_home/casc_configs"

RUN echo 2.0 > /usr/share/jenkins/ref/jenkins.install.UpgradeWizard.state

COPY official_plugins.txt /usr/share/jenkins/ref/official_plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/official_plugins.txt

USER root

# Install any certificates you might need

# WORKDIR /usr/local/share/ca-certificates
# RUN mkdir <your company>

# WORKDIR /usr/local/share/ca-certificates/zenterio
# RUN \
#  curl <URL to fetch certs> > <company>.crt && \
#  update-ca-certificates

WORKDIR /docker-java-home/jre/lib/security/
RUN \
  ../../bin/keytool -import -keystore cacerts -storepass changeit -noprompt -file /usr/local/share/ca-certificates/<company>/<company>.crt -alias <company>.root && \

RUN \
apt-get update && \
apt-get install --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" rsync

WORKDIR /
USER jenkins

RUN mkdir -p "${CASC_JENKINS_CONFIG}"
