ARG ARCH=$ARCH
ARG IMAGE_REPO=${ARCH}/debian
ARG IMAGE_VER=bullseye-slim

FROM ${IMAGE_REPO}:${IMAGE_VER}

RUN apt update && apt upgrade -y && apt install -y git python3-pip sshpass ansible

# Install ansible-server
COPY dist/*.deb /etc/ansible-server/
RUN apt install -y /etc/ansible-server/*.deb

# Set up path to use python virtual environment
ENV VIRTUAL_ENV=/opt/venvs/ansible-server
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set up Ansible
RUN printf "export ANSIBLE_CONFIG=$VIRTUAL_ENV/configuration/ansible.cfg\n" >> /root/.bashrc
RUN printf "export ANSIBLE_INVENTORY=$VIRTUAL_ENV/configuration/ssdpPlugin.json\n" >> /root/.bashrc
RUN printf "export ANSIBLE_INVENTORY_PLUGINS=$VIRTUAL_ENV/plugin\n" >> /root/.bashrc

CMD ["/bin/bash"]
