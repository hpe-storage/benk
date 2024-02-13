SHELL              := env BENK_ALMALINUX_TAG=$(BENK_ALMALINUX_TAG) $(SHELL)
BENK_ALMALINUX_TAG ?= 9.3

SHELL              := env CONTAINER_REGISTRY=$(CONTAINER_REGISTRY) $(SHELL)
CONTAINER_REGISTRY ?= quay.io/datamattsson/benk

SHELL              := env IMAGE_TAG=$(IMAGE_TAG) $(SHELL)
IMAGE_TAG          ?= v0.0.0

IMAGE=$(CONTAINER_REGISTRY):$(IMAGE_TAG)

SHELL : env PUSH=$(PUSH) $(SHELL)
PUSH ?= 

image:
	docker buildx build --platform=linux/amd64,linux/arm64 \
		--provenance=false --progress plain \
		--build-arg BENK_ALMALINUX_TAG=$(BENK_ALMALINUX_TAG) \
		$(PUSH) \
		-t $(IMAGE) .

defaults:
	env -i bash -c "PATH=\"${PATH}\" python3 src/benk/printdefaults.py" > kustomize/overlays/default/config.env
