colon := :
$(colon) := :
IMG_TAG=latest
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: arm64 amd64 package build-image create-service ansible-server-arm64-image ansible-server-amd64-image ansible-server-arm64-service ansible-server-amd64-service

arm64:
	$(eval ARCH=arm64)
	$(eval DOCKER_ARCH=arm64v8)

amd64:
	$(eval ARCH=amd64)
	$(eval DOCKER_ARCH=$(ARCH))

package:
	apt-get update && apt-get install -y build-essential debhelper devscripts equivs dh-virtualenv python3-virtualenv
	dpkg-buildpackage -us -ui -uc --buildinfo-option=-udist --buildinfo-option=-Odist/ansible-server.buildinfo --changes-option=-udist --changes-option=-Odist/ansible-server.changes

build-image:
	docker build $(ROOT_DIR) --file Dockerfile --tag ferenj/gss-ansible-server-$(ARCH)$(:)$(IMG_TAG) --build-arg ARCH=$(DOCKER_ARCH)

create-service:
	@cat $(ROOT_DIR)/service/ansible-server.service.template | TAG=$(IMG_TAG) ARCH=$(ARCH) DOCKER_ARCH=$(DOCKER_ARCH) envsubst

ansible-server-arm64-image: arm64 package build-image

ansible-server-amd64-image: amd64 package build-image

ansible-server-arm64-service: arm64 create-service

ansible-server-amd64-service: amd64 create-service
