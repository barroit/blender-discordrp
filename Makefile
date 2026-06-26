# SPDX-License-Identifier: GPL-3.0-or-later

m4 ?= m4
m4 := $(m4) -P

onchange ?= onchange

src-glob := __init__.py lib/*.py probe/*.py blender_manifest.toml LICENSES/*
obj-y := $(addprefix build/,$(wildcard $(src-glob)))

.PHONY: preprocess hot-preprocess

preprocess:

hot-preprocess: preprocess
	$(onchange) $(patsubst %,'%',$(src-glob)) -- make -j preprocess

preprocess: $(obj-y)

build/%.py: lib/pp.m4 %.py
	@mkdir -p $(@D)
	$(m4) $^ >$@

build/%: %
	@mkdir -p $(@D)
	cp $< $@

clean:
	rm -rf build
