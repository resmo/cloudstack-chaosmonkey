build:
	docker build -t cs-chaosmonkey .
run:
	docker run -it --rm --name chaosmonkey \
	-e "CLOUDSTACK_ENDPOINT=$(CLOUDSTACK_ENDPOINT)" \
	-e "CLOUDSTACK_KEY=$(CLOUDSTACK_KEY)" \
	-e "CLOUDSTACK_SECRET=$(CLOUDSTACK_SECRET)" \
	-e "CHAOSMONKEY_GROUP=$(CHAOSMONKEY_GROUP)" \
	cs-chaosmonkey
