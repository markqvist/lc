all: release

clean:
	@echo Cleaning...
	@-rm -rf ./build
	@-rm -rf ./dist
	@-rm -rf ./*.data
	@-rm -rf ./__pycache__
	@-rm -rf ./lc/__pycache__
	@-rm -rf ./*.egg-info
	@echo Done

build_sdist:
	python3 setup.py sdist

build_wheel:
	python3 setup.py bdist_wheel

documentation:
	make -C docs html

manual:
	make -C docs latexpdf epub

build_spkg: remove_symlinks build_sdist create_symlinks

release: build_sdist build_wheel

debug: remove_symlinks build_wheel
