#!/usr/bin/make -f
# -*- makefile -*-

build: clean
	-cd where; python setup.py build_ext --inplace
	-cd where; python3 setup.py build_ext --inplace
	cp ./where/*.so ./

clean:
	-rm ./*.so
	-rm ./where/*.so
