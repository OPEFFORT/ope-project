# this was seeded from https://github.com/umsi-mads/education-notebook/blob/master/Makefile
.PHONY: help build ope root push publish lab nb python-versions distro-versions image-sha clean
.IGNORE: ope root

# see if there is a specified customization in the base settting
SHELL := /bin/bash
CUST := $(shell if  [[ -a base/customization_name ]]; then cat base/customization_name;  fi)


# Name of the repository
OPE_CONTAINER_NAME := $(shell cat base/ope_container_name)

# USER id
OPE_UID := $(shell cat base/ope_uid)
# GROUP id
OPE_GID := $(shell cat base/ope_gid)
# GROUP name
OPE_GROUP := $(shell cat base/ope_group)


BASE_REG := $(shell cat base/base_registry)/
BASE_IMAGE := $(shell cat base/base_image)
BASE_TAG := $(shell cat base/base_tag)

DATE_TAG := $(shell date +"%m.%d.%y_%H.%M.%S")


# User can be an organization, 
OPE_BOOK_USER := $(shell if  [[ -a base/ope_book_user ]]; then cat base/ope_book_user; else echo ${USER}; fi)
OPE_BOOK_REG := $(shell cat base/ope_book_registry)/

OPE_BOOK_IMAGE := $(OPE_BOOK_USER)/$(OPE_CONTAINER_NAME)

OPE_BETA_TAG := :beta-$(CUST)
OPE_PUBLIC_TAG := :$(CUST)

BASE_DISTRO_PACKAGES := $(shell cat base/distro_pkgs)
PYTHON_PREREQ_VERSIONS := $(shell cat base/python_prereqs)
PYTHON_INSTALL_PACKAGES := $(shell cat base/python_pkgs)
PIP_INSTALL_PACKAGES := $(shell cat base/pip_pkgs)

# Why if for second and not first?
JUPYTER_ENABLE_EXTENSIONS := $(shell cat base/jupyter_enable_exts)
JUPYTER_DISABLE_EXTENSIONS := $(shell if  [[ -a base/jupyter_disable_exts  ]]; then cat base/jupyter_disable_exts; fi) 


# Set customization 
CUSTOMIZE_FROM := $(shell if  [[ -a base/customize_from ]]; then cat base/customize_from; else echo ${OPE_BOOK_REG}${OPE_BOOK_IMAGE}; fi)

# <reg>/<ope_project>:<ope_container>-<stable|test>-<customization>-<latest|date>
# quay.io/ucsls:stable-ucsls-burosa2023prod-latest

CUSTOMIZE_NAME := $(CUSTOMIZE_FROM)-test-$(shell cat base/customize_name) 

CUSTOMIZE_UID := $(shell cat base/customize_uid)
CUSTOMIZE_GID := $(shell cat base/customize_gid)
CUSTOMIZE_GROUP := $(shell cat base/customize_group)


# we mount here to match openshift
MOUNT_DIR := $(shell cat base/mount_dir)
HOST_DIR := ${HOME}

# extra directories to fix permissions on
EXTRA_CHOWN := $(shell if  [[ -a base/extra_chown  ]]; then cat base/extra_chown; fi) 

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: DARGS ?= --build-arg FROM_REG=$(BASE_REG) \
                   --build-arg FROM_IMAGE=$(BASE_IMAGE) \
                   --build-arg FROM_TAG=$(BASE_TAG) \
                   --build-arg OPE_UID=$(OPE_UID) \
                   --build-arg OPE_GID=$(OPE_GID) \
                   --build-arg OPE_GROUP=$(OPE_GROUP) \
                   --build-arg ADDITIONAL_DISTRO_PACKAGES="$(BASE_DISTRO_PACKAGES)" \
                   --build-arg PYTHON_PREREQ_VERSIONS="$(PYTHON_PREREQ_VERSIONS)" \
                   --build-arg PYTHON_INSTALL_PACKAGES="$(PYTHON_INSTALL_PACKAGES)" \
                   --build-arg PIP_INSTALL_PACKAGES="$(PIP_INSTALL_PACKAGES)" \
				   --build-arg EXTRA_CHOWN="$(EXTRA_CHOWN)"
build: ## Make the image customized appropriately
	docker build $(DARGS) $(DCACHING) -t $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG) --file base/Build.Dockerfile base
	
customize: DARGS ?= --build-arg FROM_IMAGE=$(CUSTOMIZE_FROM) \
                   --build-arg CUSTOMIZE_UID=$(CUSTOMIZE_UID) \
                   --build-arg CUSTOMIZE_GID=$(CUSTOMIZE_GID) \
                   --build-arg CUSTOMIZE_GROUP=$(CUSTOMIZE_GROUP) \
		           --build-arg EXTRA_CHOWN="$(EXTRA_CHOWN)"
customize:  ## build a customized deployment image
	docker build $(DARGS) $(DCACHING) --rm --force-rm -t $(CUSTOMIZE_NAME) --file base/Customize.Dockerfile base 
	docker-squash -t $(CUSTOMIZE_NAME) $(CUSTOMIZE_NAME)

push: DARGS ?=
push: ## push private build
# make dated version
	docker tag  $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG) $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG)_$(DATE_TAG)
# push to private image repo
	docker push $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG)_$(DATE_TAG)
# push to update tip to current version
	docker push $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG)

pull-beta: DARGS ?=
pull-beta: ## pull most recent private version
	docker pull $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG)

publish: pull-beta
publish: DARGS ?=
publish: ## publish current private build to public published version
# make dated version
	docker tag $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG) $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_PUBLIC_TAG)_$(DATE_TAG)
# push to private image repo
	docker push $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_PUBLIC_TAG)_$(DATE_TAG)
# copy to tip version
	docker tag $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG) $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_PUBLIC_TAG)
# push to update tip to current version
	docker push $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_PUBLIC_TAG)

checksum: ARGS ?= find / -not \( -path /proc -prune \) -not \( -path /sys -prune \) -type f -exec stat -c '%n %a' {} + | LC_ALL=C sort | sha256sum | cut -c 1-64
checksum: DARGS ?= -u 0
checksum: ## start private version  with root shell to do admin and poke around
	@-docker run -i --rm $(DARGS) $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG) $(ARGS)

run-beta: ARGS ?=
run-beta: DARGS ?= -u $(OPE_UID):$(OPE_GID) -v "${HOST_DIR}":"${MOUNT_DIR}" -v "${SSH_AUTH_SOCK}":"${SSH_AUTH_SOCK}" -v "${SSH_AUTH_SOCK}":"${SSH_AUTH_SOCK}" -e SSH_AUTH_SOCK=${SSH_AUTH_SOCK} -p ${SSH_PORT}:22
run-beta: PORT ?= 8888
run-beta: ## start published version with jupyter lab interface
	docker run -i --rm -p $(PORT):$(PORT) $(DARGS) $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG) $(ARGS)

show-tag: ARGS ?=
show-tag: DARGS ?=
show-tag: ## tag current private build as beta
	@-echo $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG)
  

### DEBUG TARGETS
root: ARGS ?= /bin/bash
root: DARGS ?= -u 0
root: ## start private version  with root shell to do admin and poke around
	-docker run -it --rm $(DARGS) $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG) $(ARGS)

user: ARGS ?= /bin/bash
user: DARGS ?=
user: ## start private version with usershell to poke around
	-docker run -it --rm $(DARGS) $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_BETA_TAG) $(ARGS)


### PUBLIC USAGE TARGETS
pull: 
pull: ## pull most recent public version
	docker pull $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_PUBLIC_TAG)

# TODO: Cut out SSH port
run: pull
run: ARGS ?=
run: DARGS ?= -u $(OPE_UID):$(OPE_GID) -v "${HOST_DIR}":"${MOUNT_DIR}" -v "${SSH_AUTH_SOCK}":"${SSH_AUTH_SOCK}" -v "${SSH_AUTH_SOCK}":"${SSH_AUTH_SOCK}" -e SSH_AUTH_SOCK=${SSH_AUTH_SOCK}
run: PORT ?= 8888
run: ## start published version with jupyter lab interface
	docker run -it --rm -p $(PORT):$(PORT) $(DARGS) $(OPE_BOOK_REG)$(OPE_BOOK_IMAGE)$(OPE_PUBLIC_TAG) $(ARGS) 

run-cust: ARGS ?=
run-cust: DARGS ?= -u $(CUSTOMIZE_UID):$(CUSTOMIZE_GID) -v "${HOST_DIR}":"${MOUNT_DIR}" -v "${SSH_AUTH_SOCK}":"${SSH_AUTH_SOCK}" -v "${SSH_AUTH_SOCK}":"${SSH_AUTH_SOCK}" -e SSH_AUTH_SOCK=${SSH_AUTH_SOCK} 
run-cust: PORT ?= 8888
run-cust: ## start published version with jupyter lab interface
	docker run -it --rm -p $(PORT):$(PORT) $(DARGS) $(CUSTOMIZE_NAME) $(ARGS)