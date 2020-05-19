PYTHON = python
PIP = pip

REPO_PREFIX = devhub-docker.cisco.com/nextgen-cpo-docker-dev-local/
IMAGE_NAME = ad-python3

# lambda function name - may need to change for each project.
LAMBDA_FUNCTION_NAME = python3-activities

# lambda zip file - will be overridden by build process.
LAMBDA_ZIP = lambda.zip


.PHONY: all  ## run a full build
all: clean linux mocks test

.PHONY: create-certs
create-certs:
	@echo "Creating Selfsigned certs"
	mkdir -p secrets/ssl/cert
	touch secrets/ssl/cert/.disable_cert_validation
	/usr/bin/openssl req -x509 -newkey rsa:2048 -nodes -keyout secrets/ssl/cert/private_key.pem -out secrets/ssl/cert/certificate.pem -days 365 -subj "/C=US/ST=Texas/L=Austin/O=Cisco/OU=longhorn/CN=python"



.PHONY: docker
docker:  ## build docker image
	@echo "Building docker image"
	docker build -t $(REPO_PREFIX)$(IMAGE_NAME):localdeploy .

.PHONY: linux
linux: docker  ## build linux distribution
	@echo "Building function worker (linux)"
	$(PYTHON) --version
	$(PYTHON) setup.py bdist_wheel

.PHONY: build
build: linux  ## run the build

.PHONY: buildtest
buildtest: ## build docker image for testing
	@echo "Building test image"
	docker build --target=builder -t $(IMAGE_NAME):testing .

.PHONY: flake8
flake8: buildtest  ## run flake8 test
	@echo "Running flake8"
	docker run --rm -t $(IMAGE_NAME):testing flake8

.PHONY: test
test: flake8 ## run unit tests
	@echo "Running Unit Tests"
	docker run --rm -t -v $(PWD):/report $(IMAGE_NAME):testing \
		bash -c "coverage run setup.py test && coverage xml -o /report/cobertura-coverage.xml"

.PHONY: staticanalysis
staticanalysis: flake8 ## run static analysis
	@echo "Running Static Analysis"
	docker run --rm -t $(IMAGE_NAME):testing pylint activities_python functions/$(LAMBDA_FUNCTION_NAME)/*

.PHONY: mocks
mocks: ## run mocks
	@echo "Generating Mocks"
	@echo "No mocks to run"


.PHONY: lambda
lambda: buildtest  ## build lambda archive
	@echo "Building Lambda distribution $(LAMBDA_ZIP)..."
	mkdir -p build
	docker run --rm -t -v $(PWD)/build:/build $(IMAGE_NAME):testing pip install --upgrade /wheels/longhorn_python3_adapter-1.0-py2.py3-none-any.whl -t /build
	cp -R functions/$(LAMBDA_FUNCTION_NAME)/ build/
	pushd build && zip -r $(LAMBDA_ZIP) .

.PHONY: clean
clean:
	$(RM) -r build
	$(RM) -r dist
	$(RM) -r cobertura-coverage.xml
