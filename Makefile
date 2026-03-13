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
	@echo Done

assets:
	cp README.md GUIDE.md Chrome_Horizons.md lc/data/

build_wheel: assets
	python3 setup.py bdist_wheel

documentation:
	make -C docs html

manual:
	make -C docs latexpdf epub

build_spkg: remove_symlinks create_symlinks

release: build_wheel

debug: remove_symlinks build_wheel
