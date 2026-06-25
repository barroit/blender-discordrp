# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2026 Jiamu Sun <39@barroit.sh>
#
# https://docs.blender.org/api/current/bpy.types.Struct.html#bpy.types.Struct.properties
# https://docs.blender.org/api/current/bpy.types.EnumProperty.html#bpy.types.EnumProperty.enum_items

from ..lib.current import current
from bpy import app, ops, types, utils
from time import monotonic as time_monotonic
from types import SimpleNamespace

def find_area(window, event):
	for area in window.screen.areas:
		if area.x <= event.mouse_x <= area.x + area.width and \
		   area.y <= event.mouse_y <= area.y + area.height:
			return area.type

	return None

def do_probe(context, event):
	res = SimpleNamespace()

	area = find_area(context.window, event)
	workspace = context.window.workspace.name

	res.details = f"In {workspace}"

	if area:
		area_meta = types.Area.bl_rna.properties['type']
		editor = area_meta.enum_items[area].name

		res.details += f" ({editor})"

	if hasattr(context, 'active_object'):
		target = context.active_object.name

		res.state = f"Editing {target}"

	return res

class probe_interaction(types.Operator):
	bl_idname = 'wm.probe_interaction'
	bl_label = 'Probe Interaction'

	def invoke(self, context, event):
		self.prev = 0.390831

		context.window_manager.modal_handler_add(self)

		return { 'RUNNING_MODAL' }

	def modal(self, context, event):
		if event.type == 'LEFTMOUSE' and \
		   event.value == 'PRESS' and \
		   not app.is_job_running('RENDER') and \
		   not app.is_job_running('OBJECT_BAKE'):
			next = time_monotonic()

			if next - self.prev >= 0.5:
				self.prev = next
				current.state[0] = do_probe(context, event)

		return { 'PASS_THROUGH' }

def probe_start_interact():
	ops.wm.probe_interaction('INVOKE_DEFAULT')

def probe_enable_interact():
	utils.register_class(probe_interaction)

def probe_disable_interact():
	utils.unregister_class(probe_interaction)
