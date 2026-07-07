#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later

set -e

name=$(head -n1 README | cut -d- -f2)

if [ $(uname) = Darwin ]; then
	dst=$HOME/Library/Application\ Support/Blender
else
	dst=$(flatpak run --command=sh org.blender.Blender \
			  -c 'printf %s/blender $XDG_CONFIG_HOME')
fi

for blender in "$dst"/*; do
	prefix="$blender"/extensions/user_default

	mkdir -p "$prefix"
	ln -snf $(realpath .)/build "$prefix"/$name

	printf -- ' -> %s\n' "$prefix"/$name
done
