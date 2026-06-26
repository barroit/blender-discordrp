m4_dnl SPDX-License-Identifier: GPL-3.0-or-later
m4_dnl
m4_divert(-1)

m4_changequote(⡇, ⡇)
m4_changecom

m4_define(APP_ID, '1518963969065357342')

m4_define(IPC_MAYBE_STOP, if ipc.disabled: return)
m4_define(IPC_ASSERT_PASS, if $@: continue)

m4_divert(0)m4_dnl
