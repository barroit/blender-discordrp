# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2026 Jiamu Sun <39@barroit.sh>
#

from ..lib.current import current
from bpy import app
from types import SimpleNamespace

ctx = SimpleNamespace()

def count_frame(render):
	return (render.end - render.start) // render.step + 1

def on_render_init(scene):
	ctx.restore = current.state[0]

	ctx.start = scene.frame_start
	ctx.end = scene.frame_end
	ctx.step = scene.frame_step
	ctx.index = 0
	ctx.frames = count_frame(ctx)

def on_render_pre(scene):
	res = SimpleNamespace()

	ctx.index += 1
	res.party = SimpleNamespace()

	res.details = f"Rendering frames from {ctx.start} to {ctx.end}"
	res.state = f"Every {ctx.step} frame"
	res.party.id = 'miku'
	res.party.size = [ ctx.index, ctx.frames ]

	if ctx.step > 1:
		res.state += 's'

	current.state[0] = res

def render_complete(scene, depsgraph):
	current.state[0] = ctx.restore

def probe_enable_render():
	app.handlers.render_init.append(on_render_init)
	app.handlers.render_pre.append(on_render_pre)
	app.handlers.render_complete.append(render_complete)
	app.handlers.render_cancel.append(render_complete)

def probe_disable_render():
	app.handlers.render_init.remove(on_render_init)
	app.handlers.render_pre.remove(on_render_pre)
	app.handlers.render_complete.remove(render_complete)
	app.handlers.render_cancel.remove(render_complete)
