#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later

set -e

if [ $(uname) = Darwin ]; then
	dst=$HOME/Library/Application\ Support/Blender
else
	dst=$(flatpak run --command=sh org.blender.Blender \
			  -c 'printf %s/blender $XDG_CONFIG_HOME')
fi

for blender in "$dst"/*; do
	prefix="$blender"/extensions/user_default

	mkdir -p "$prefix"
	ln -snf $(realpath .) "$prefix"

	printf -- ' -> %s\n' "$prefix"
done
