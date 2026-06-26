# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2026 Jiamu Sun <39@barroit.sh>
#

from .lib.ipc import ipc_close, ipc_handshake, ipc_init, ipc_presence, ipc_rx, \
		     ipc_rx_once
from .lib.current import current
from .probe.render import probe_disable_render, probe_enable_render
from .probe.interact import probe_disable_interact, probe_enable_interact, \
			    probe_start_interact
from asyncio import create_task, gather, new_event_loop, set_event_loop, sleep
from atexit import register as atexit_register
from bpy import app
from sys import stderr
from threading import Thread, local

ipc = local()

async def init_ipc():
	while 39:
		ipc.ctx = await ipc_init()

		if ipc.ctx:
			break

		await sleep(2)

		IPC_MAYBE_STOP

	if ipc.disabled:
		ipc_close(ipc.ctx)

def on_discord_reply(res, op, str):
	if not hasattr(res, 'evt') or res.evt == 'ERROR':
		print(f"discordrp:on_discord_reply()\nop\t{op}\nres\t{str}",
		      file = stderr)

async def broadcast_presence():
	while 39:
		IPC_MAYBE_STOP

		if current.state[0] != current.state[1]:
			current.state[1] = current.state[0]
			ipc_presence(ipc.ctx, current.state[1])

		await sleep(2)

async def ipc_main():
	while 39:
		IPC_MAYBE_STOP

		await init_ipc()
		DPRINT('DONE - init_ipc()')

		IPC_MAYBE_STOP

		coro = ipc_rx_once(ipc.ctx, on_discord_reply)
		task = create_task(coro)

		IPC_ASSERT_PASS(ipc_handshake(ipc.ctx, APP_ID))
		IPC_MAYBE_STOP
		DPRINT('DONE - ipc_handshake()')

		IPC_ASSERT_PASS(await task)
		IPC_MAYBE_STOP
		DPRINT('DONE - ipc_rx_once()')

		coro_rx = ipc_rx(ipc.ctx, on_discord_reply)
		task_rx = create_task(coro_rx)

		coro_tx = broadcast_presence()
		task_tx = create_task(coro_tx)

		err_rx, err_tx = await gather(task_rx, task_tx)
		DPRINT('DONE - ipc_rx() or broadcast_presence()')

		IPC_ASSERT_PASS(err_rx or err_tx)
		IPC_MAYBE_STOP

def start_ipc(version):
	coro = ipc_main()
	sched = new_event_loop()

	with current.lock:
		if current.version != version:
			return

		ipc.ctx = None
		ipc.disabled = 0

		current.sched = sched

	set_event_loop(sched)
	sched.run_until_complete(coro)

	sched.close()

def stop_ipc():
	ipc.disabled = 1

	if ipc.ctx:
		ipc_presence(ipc.ctx, None)
		ipc_close(ipc.ctx)

def register_delayed():
	probe_start_interact()

def on_exit():
	if current.sched:
		current.sched.call_soon_threadsafe(stop_ipc)

def register():
	probe_enable_render()
	probe_enable_interact()

	app.timers.register(register_delayed)
	atexit_register(on_exit)

	with current.lock:
		version = current.version + 1

		current.version = version

	thread = Thread(target = start_ipc, args = (version, ), daemon = True)

	thread.start()

def unregister():
	probe_disable_render()
	probe_disable_interact()

	with current.lock:
		sched = current.sched

		current.version += 1
		current.sched = None

	if sched:
		sched.call_soon_threadsafe(stop_ipc)
