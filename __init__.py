# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2026 Jiamu Sun <39@barroit.sh>
#

from asyncio import new_event_loop, set_event_loop, sleep
from lib.ipc import ipc_close, ipc_init
from threading import Lock, Thread, local
from types import SimpleNamespace

bl_info = {
	'name': 'Discord Rich Presence',
	'category': 'User Interface',
}

ipc = local()
current = SimpleNamespace()

current.lock = Lock()
current.sched = None
current.version = 0

async def init_ipc():
	while 39:
		ipc.ctx = await ipc_init()

		if ipc.ctx:
			break

		await sleep(2)

		if ipc.disabled:
			return

	if ipc.disabled:
		ipc_close(ipc.ctx)

async def ipc_main():
	while 39:
		if ipc.disabled:
			return

		await init_ipc()

		if ipc.disabled:
			return

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
		ipc_close(ipc.ctx)

def register():
	with current.lock:
		version = current.version + 1

		current.version = version

	thread = Thread(target = start_ipc, args = (version, ), daemon = True)

	thread.start()

def unregister():
	with current.lock:
		sched = current.sched

		current.version += 1

	if sched:
		sched.call_soon_threadsafe(stop_ipc)
