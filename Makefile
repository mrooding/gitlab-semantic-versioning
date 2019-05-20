# Author: noi.narisak@gmail.com
# Date: 2019-05-14
# Desc: Makefile used for working with Docker container.

.PHONY: help build run clean rebuild publish

CONTAINER_NAME=gitlab-semantic-versioning
CONTAINER_VERSION=v1.0.0
CONTAINER=${CONTAINER_NAME}:${CONTAINER_VERSION}
include .env
DOCKERHUB_USERNAME=noinarisak

help: ## This help. Inspired by http://bit.ly/2EKRAH4
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

build: ## Build docker image.
	@docker build -t ${CONTAINER} .

run: build ## Run docker image.
	@docker run -it -v "$$(pwd)":/data ${CONTAINER} /bin/bash

clean: ## Clean docker images.
	-@docker rmi -f ${CONTAINER} &> /dev/null || true
	-@docker rmi -f ${DOCKERHUB_USERNAME}/${CONTAINER} &> /dev/null || true

rebuild: clean build ## Rebuild.

publish: clean build ## Publish.
	@docker login --username ${DOCKERHUB_USERNAME} --password ${DOCKERHUB_PASSWORD}
	@docker tag ${CONTAINER} ${DOCKERHUB_USERNAME}/${CONTAINER}
	@docker push ${DOCKERHUB_USERNAME}/${CONTAINER}
