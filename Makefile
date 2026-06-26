# SPDX-License-Identifier: GPL-3.0-or-later

m4 ?= m4
m4 := $(m4) -P

src := __init__.py $(wildcard lib/*.py probe/*.py) \
       blender_manifest.toml LICENSES/GPL-3.0-or-later

obj-y := $(addprefix build/,$(src))

.PHONY: preprocess
preprocess: $(obj-y)

build/%.py: lib/pp.m4 %.py
	@mkdir -p $(@D)
	$(m4) $^ >$@

build/%: %
	@mkdir -p $(@D)
	cp $< $@
