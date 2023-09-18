.PHONY: all install format build test

all: install format build test

install:
	npm install

format:
	npm run format

build:
	npm run build

test:
	npm run test-coverage
