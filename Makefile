all: release

clean:
	@echo Cleaning...
	@-rm -rf ./build
	@-rm -rf ./dist
	@-rm -rf ./lc/data/*
	@touch ./lc/data/.keep
	@-rm -rf ./*.data
	@-rm -rf ./__pycache__
	@-rm -rf ./lc/__pycache__
	@-rm -rf ./*.egg-info
	@-rm -rf ./lc/data/*.md
	@-rm -rf ./lc/data/examples
	@echo Done

assets:
	cp README.md GUIDE.md CHRONICLES.md Chrome_Horizons.md lc/data/
	cp -rv docs/examples lc/data/

build_wheel: assets
	python3 setup.py bdist_wheel

documentation:
	make -C docs html

manual:
	make -C docs latexpdf

build_spkg: remove_symlinks create_symlinks

release: build_wheel

debug: remove_symlinks build_wheel
