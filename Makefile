all:

clean: /dev/null
	rm -f distribute-*.tar.gz distribute-*.egg
	rm -rf nose-*.egg
	rm -rf *.egg-info
	rm -rf build dist
	find . -name '*.pyc' -print0 | xargs -0 rm -f