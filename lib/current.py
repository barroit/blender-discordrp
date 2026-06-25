# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2026 Jiamu Sun <39@barroit.sh>
#

from threading import Lock
from types import SimpleNamespace

current = SimpleNamespace()

current.lock = Lock()
current.sched = None
current.version = 0
current.state = [ None, None ]

current.state[0] = SimpleNamespace()
current.state[1] = SimpleNamespace()
