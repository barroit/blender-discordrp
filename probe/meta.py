# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2026 Jiamu Sun <39@barroit.sh>
#

import bpy
from ..lib.current import current
from bpy import app as bpy_app
from os.path import basename, dirname, isfile, splitext
from types import SimpleNamespace

def try_readme_header(path, fallback):
	with open(path, 'r', encoding = 'utf-8') as stream:
		first = stream.readline().rstrip('\n')
		second = stream.readline().rstrip('\n')

	if second == '=' * len(first):
		return first

	return fallback

def normalize_name(path):
	file = basename(path)
	name = splitext(file)[0]

	return name

def probe_meta():
	res = SimpleNamespace()
	platform = bpy_app.build_platform.decode('utf-8')
	project = 'Untitled'
	delay = 1

	if hasattr(bpy.data, 'filepath') and bpy.data.filepath:
		delay = 5
		project = normalize_name(bpy.data.filepath)

		dir = dirname(bpy.data.filepath)
		readme = f"{dir}/README"

		if isfile(readme):
			project = try_readme_header(readme, project)

	res.name = 'Blender'
	res.assets = SimpleNamespace()

	res.assets.large_text = f"{bpy_app.version_string} - {platform}"
	res.assets.large_image = 'CDN_MATERIAL_ICON/blender.png'

	res.assets.small_text = project.replace('_', ' ')
	res.assets.small_image = 'CDN_MATERIAL_ICON/document.png'

	current.state[2] = res
	return delay

def probe_enable_meta():
	probe_meta()
	bpy_app.timers.register(probe_meta, persistent = True)

def probe_disable_meta():
	bpy_app.timers.unregister(probe_meta)
