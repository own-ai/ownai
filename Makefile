.PHONY: all install format lint build test

all: install format lint build test

install:
	npm install

format:
	npm run format

lint:
	npm run lint

build:
	npm run build

test:
	npm run test-coverage
