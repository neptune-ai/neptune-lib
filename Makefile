clean:
	rm -fr dist/ VERSION
build:
	python setup.py git_version sdist

