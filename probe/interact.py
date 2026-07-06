# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2026 Jiamu Sun <39@barroit.sh>
#
# https://docs.blender.org/api/current/bpy.types.Struct.html#bpy.types.Struct.properties
# https://docs.blender.org/api/current/bpy.types.EnumProperty.html#bpy.types.EnumProperty.enum_items

from ..lib.current import current
from bpy import app, context as __context, ops, types, utils
from bpy.app.handlers import persistent
from collections import deque
from types import SimpleNamespace

def find_area(window, axis):
	for area in window.screen.areas:
		if area.x <= axis[0] <= area.x + area.width and \
		   area.y <= axis[1] <= area.y + area.height:
			return area.type

	return None

def format_message(context, axis):
	res = SimpleNamespace()

	area = find_area(context.window, axis)
	workspace = context.window.workspace.name

	res.details = f"In {workspace}"

	if area:
		area_meta = types.Area.bl_rna.properties['type']
		editor = area_meta.enum_items[area].name

		res.details += f" ({editor})"

	if hasattr(context, 'active_object') and context.active_object:
		target = context.active_object.name

		res.state = f"Editing {target}"

	return res

class probe_interaction(types.Operator):
	bl_idname = 'wm.probe_interaction'
	bl_label = 'Probe Interaction'

	def invoke(self, context, event):
		event_timer_add = context.window_manager.event_timer_add
		modal_handler_add = context.window_manager.modal_handler_add
		timer = event_timer_add(1, window = context.window)

		self.clicks = deque()
		probe_interaction.timer = timer

		modal_handler_add(self)
		return { 'RUNNING_MODAL' }

	def modal(self, context, event):
		if event.type == 'TIMER' and len(self.clicks):
			axis = self.clicks.popleft()

			current.state[0] = format_message(context, axis)
			return { 'RUNNING_MODAL' }

		elif event.type in ( 'LEFTMOUSE', 'RIGHTMOUSE' ) and \
		   event.value == 'RELEASE' and \
		   not app.is_job_running('RENDER') and \
		   not app.is_job_running('OBJECT_BAKE'):
			self.clicks.append(( event.mouse_x, event.mouse_y ))

		return { 'PASS_THROUGH' }

def probe_start_interact():
	ops.wm.probe_interaction('INVOKE_DEFAULT')

@persistent
def on_load_post(filepath):
	probe_start_interact()

def __probe_enable_interact():
	utils.register_class(probe_interaction)
	app.timers.register(probe_start_interact)
	app.handlers.load_post.append(on_load_post)

def __probe_disable_interact():
	__context.window_manager.event_timer_remove(probe_interaction.timer)
	utils.unregister_class(probe_interaction)
	app.handlers.load_post.remove(on_load_post)

def probe_enable_interact():
	if not app.background:
		__probe_enable_interact()

def probe_disable_interact():
	if not app.background:
		__probe_disable_interact()
