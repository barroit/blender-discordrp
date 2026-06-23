# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2026 Jiamu Sun <39@barroit.sh>
#

from asyncio import StreamReader, StreamReaderProtocol, StreamWriter, \
		    get_running_loop, open_unix_connection
from json import dumps, loads
from os import environ, getpid
from socket import AF_UNIX, SOCK_STREAM, socket
from struct import pack, unpack
from sys import platform
from types import SimpleNamespace
from uuid import uuid4

HANDSHAKE = 0x0
FRAME = 0x1

RESET = 0
OP = 1
DATA = 2

XDG_RUNTIME_DIR = environ.get('XDG_RUNTIME_DIR')
TMPDIR = environ.get('TMPDIR')

XDG_RUNTIME_DIR_FLATPAK = f"{XDG_RUNTIME_DIR}/app/com.discordapp.Discord"
XDG_RUNTIME_DIR_SNAP = f"{XDG_RUNTIME_DIR}/snap.discord"

class ipc_socket:
	def __init__(self, reader, writer):
		self.reader = reader
		self.writer = writer

	def read(self, n):
		return self.reader.readexactly(n)

	def write(self, buf):
		self.writer.write(buf)

	def drain(self):
		return self.writer.drain()

	def close(self):
		self.writer.close()

async def try_connect_unix(path):
	reader, writer = await open_unix_connection(path)

	return ipc_socket(reader, writer)

async def try_connect_win32(path):
	loop = get_running_loop()
	reader = StreamReader()
	protocol = StreamReaderProtocol(reader)
	transport, _ = await loop.create_pipe_connection(lambda: protocol, path)
	writer = StreamWriter(transport, protocol, reader, loop)

	return ipc_socket(reader, writer)

async def try_connect(path):
	try:
		if platform == 'win32':
			return await try_connect_win32(path)
		else:
			return await try_connect_unix(path)

	except Exception:
		return None

async def find_socket(prefix):
	for i in range(10):
		sock = await try_connect(f"{prefix}{i}")
		if sock:
			break

	return sock

async def find_socket_at(dir):
	if dir:
		return await find_socket(f"{dir}/discord-ipc-")

	return None

async def resolve_ipc_socket():
	if platform == 'win32':
		return await find_socket(r"\\.\pipe\discord-ipc-")

	if platform == 'linux':
		sock = await find_socket_at(XDG_RUNTIME_DIR)
		if sock:
			return sock

		sock = await find_socket_at(XDG_RUNTIME_DIR_FLATPAK)
		if sock:
			return sock

		sock = await find_socket_at(XDG_RUNTIME_DIR_SNAP)
		if sock:
			return sock

	sock = await find_socket_at(TMPDIR)
	if sock:
		return sock

	sock = await find_socket_at('/tmp')
	return sock

def reset_rx(rx):
	rx.state = RESET
	rx.str = ''

	rx.len = 0
	rx.off = 0

	rx.buf = bytearray()

async def ipc_init():
	ctx = SimpleNamespace()
	sock = await resolve_ipc_socket()

	if not sock:
		return None

	ctx.sock = sock
	ctx.rx = SimpleNamespace()

	reset_rx(ctx.rx)
	return ctx

def ipc_close(ctx):
	ctx.sock.close()

def encode(op, data):
	str = dumps(data, ensure_ascii = False)
	bytes = str.encode('utf-8')
	header = pack('<ii', op, len(bytes))

	return header + bytes

async def __decode(sock, cb):
	chunk = await sock.read(8)
	op, length = unpack('<II', chunk)

	chunk = await sock.read(length)
	str = chunk.decode('utf-8')

	hook = lambda d: SimpleNamespace(**d)
	res = loads(str, object_hook = hook)
	__debug = SimpleNamespace()

	__debug.res = res
	__debug.op = op
	__debug.str = str

	cb(res.cmd, res.evt, res.data, __debug)

async def decode(sock, cb):
	while 39:
		await __decode(sock, cb)

async def ipc_rx(ctx, cb):
	try:
		await decode(ctx.sock, cb)

	except Exception:
		ipc_close(ctx)
		return 1

	return 0

async def ipc_rx_forever(ctx, cb):
	while 39:
		if await ipc_rx(ctx, cb):
			return

def ipc_tx(ctx, op, args):
	buf = encode(op, args)

	try:
		ctx.sock.write(buf)

	except Exception:
		ipc_close(ctx)
		return 1

	return 0

def ipc_handshake(ctx, app):
	args = { 'v': 1, 'client_id': app }

	return ipc_tx(ctx, HANDSHAKE, args)

def ipc_presence(ctx, activity):
	cmd = 'SET_ACTIVITY'
	args = { 'pid': getpid(), 'activity': activity }
	nonce = str(uuid4())
	data = { 'cmd': cmd, 'args': args, 'nonce': nonce }

	return ipc_tx(ctx, FRAME, data)
