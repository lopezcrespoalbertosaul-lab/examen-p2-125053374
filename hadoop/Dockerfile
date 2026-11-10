FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    openssh-server \
    openssh-client \
    rsync \
    python3 \
    python3-pip \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

# SSH sin contrasena
RUN ssh-keygen -t rsa -P '' -f /root/.ssh/id_rsa && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 0600 /root/.ssh/authorized_keys && \
    echo "Host localhost\n   StrictHostKeyChecking no\n" >> /root/.ssh/config && \
    echo "Host *\n   StrictHostKeyChecking no\n" >> /root/.ssh/config

# Instalacion de Hadoop
RUN curl -o hadoop.tar.gz https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xzf hadoop.tar.gz -C /opt/ && \
    mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} && \
    rm hadoop.tar.gz

RUN pip3 install --no-cache-dir requests

WORKDIR /workspace

CMD service ssh start && tail -f /dev/null