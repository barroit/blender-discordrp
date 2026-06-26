m4_dnl SPDX-License-Identifier: GPL-3.0-or-later
m4_dnl
m4_divert(-1)

m4_changequote(⡇, ⡇)
m4_changecom

m4_define(CDN_ROOT, https://cdn.jsdelivr.net/gh/barroit)
m4_define(CDN_MATERIAL_ICON, CDN_ROOT/vscode-material-icon-theme@master/icons)

m4_define(APP_ID, '1518963969065357342')

m4_define(IPC_MAYBE_STOP, if ipc.disabled: return)
m4_define(IPC_ASSERT_PASS, if $@: continue)

m4_syscmd(env | grep -q ^NDEBUG=)
m4_define(DPRINT, m4_ifelse(m4_sysval, 0, , print($@)))

m4_divert(0)m4_dnl
