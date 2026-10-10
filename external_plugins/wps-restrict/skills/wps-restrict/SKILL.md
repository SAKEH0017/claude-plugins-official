---
name: wps-restrict
description: Restrict WPS Office on Windows to stop background activity, kill network access, disable auto-start, remove cloud-drive icons, and reclaim disk space. Use this skill whenever the user mentions WPS Office (WPS 文字 / 表格 / 演示 / WPS Cloud / 金山文档 / WPS365 / Kingsoft / ksomisc / wpscloudsvr / promecefpluginhost), wants to disable WPS background processes, block WPS network access, remove WPS from File Explorer, prevent WPS auto-startup, clean WPS disk usage, or complains about WPS popups / ads / cloud sync. Triggers on phrases like "限制 WPS", "防止 WPS 自启", "阻止 WPS 联网", "删 WPS 图标", "WPS 占空间", "WPS 弹广告", "wps-restrict". Windows-only. Not for Microsoft Office (Word/Excel) or for WPS document editing itself.
---

# wps-restrict

Comprehensive toolkit for restricting WPS Office on Windows. Combines six layers of restrictions with full reversibility.

## What this skill does

WPS Office is notorious for: background services that re-enable themselves, an embedded Chromium component (CEF) that bypasses main-process firewall rules, scheduled tasks that launch WPS on login, a service (`wpscloudsvr`) that calls home, a cloud-drive that injects icons into File Explorer, and gigabytes of cached data. Single-point fixes don't work — WPS heals itself. This skill applies **defense in depth**: each layer can fail and the others still hold.

## When to use

Invoke this skill when the user wants ANY of:
- Stop WPS from running in the background
- Block WPS from accessing the network (ads, telemetry, cloud sync, updates)
- Prevent WPS from auto-starting at login
- Remove WPS cloud-drive icons from File Explorer / Quick Access / Navigation Pane
- Clean up disk space consumed by WPS
- Reduce WPS popup ads and "recommendations"
- Audit what WPS is doing on their machine

Do NOT invoke for: Microsoft Office (Word/Excel/PowerPoint) issues, Mac/Linux WPS, or editing WPS documents.

## Required permissions

The skill auto-detects whether the current PowerShell session is elevated. Some operations require **administrator** (UAC prompt):
- Creating firewall rules
- Disabling scheduled tasks
- Disabling Windows services
- Deleting HKLM registry entries

If a step needs admin, the script tells the user to re-run from an elevated PowerShell. Non-admin steps work in any PowerShell.

## Layered restriction model

The skill applies restrictions in this order. Each step is independent and reversible.

### Layer 1 — Firewall (kills all WPS network access)

Creates outbound-block rules for the WPS executables. Bind to absolute path so version upgrades don't break the rules.

Target processes (7):
- `wps.exe` — main UI process
- `wpscenter.exe` — control panel
- `wpscloudsvr.exe` — cloud sync service host
- `wpscloudlaunch.exe` — cloud launch helper
- `ksomisc.exe` — Kingsoft miscellaneous daemon
- `promecefpluginhost.exe` — **embedded Chromium subprocess** (commonly missed by other guides; it can bypass main-process firewall)
- `wpscloudsv.exe` — older cloud variant

Firewall rules are created via `New-NetFirewallRule` with `-Direction Outbound -Action Block`. To undo: `Remove-NetFirewallRule -DisplayName "Block WPS - *"`.

### Layer 2 — WPS configuration files (kills recommendations, ads, cloud, updates)

WPS reads `Enable*=0` settings from INI files in `%APPDATA%\Kingsoft\WPS\Desktop\config\`. Writing all 8 settings to 0 disables:

| Setting | Effect when 0 |
|---|---|
| `EnableCloud` | No cloud sync, no cloud docs, no cloud templates |
| `EnableAutoUpdate` | No background update checks |
| `EnableStartupBoot` | WPS won't ask to enable boot-start |
| `EnableRecommend` | No template recommendations |
| `EnableAd` | No popup ads |
| `EnablePersonalCenter` | No avatar / member center |
| `EnableHotspotNews` | No "hot news" feed |
| `EnableKuaKan` | No cross-device "quick view" |

INI files are written atomically (preserves other settings). When done, first launch of WPS will rebuild missing settings without overwriting these.

### Layer 3 — Scheduled tasks (kills auto-launch)

Disables 3 WPS scheduled tasks that auto-launch WPS components:
- `WpsUpdateLogonTask_<username>` — runs on user login
- `WpsUpdateTask_<username>` — runs on schedule
- `WpsWakeWnsLogonTask` — wake-from-sleep trigger

⚠ **WPS has a self-heal mechanism**: when WPS starts, it re-enables these tasks. So this layer alone is insufficient — must be combined with Layer 4 (service) and Layer 1 (firewall) for the healing to be harmless.

### Layer 4 — Windows service (kills the system-level anchor)

Disables the `wpscloudsvr` service. By default it is `Manual` (not Disabled), which means Windows can start it on demand. Setting to `Disabled` prevents this.

The service is registered with a path that may point to a leftover `C:\Program Files (x86)\Kingsoft\office6\wpscloudsvr.exe` even when the real install is on another drive. This is normal — WPS still runs from the real path when launched.

### Layer 5 — Disk cleanup (reclaims space)

WPS accumulates:
- `office6\cache` (~40 MB) — render/spellcheck cache
- `office6\log` (~16 MB) — logs
- `wps\addons\pool` (~750 MB) — plugin version pool (WPS-downloaded versions; deleting this is risky if firewall is also blocking WPS, since WPS cannot re-download)
- `addons\` (~700 MB) — WPS modules (deleting breaks specific features)
- `C:\Users\<user>\WPSDrive\` (~few MB) — cloud local cache

The skill provides read-only analysis first, then offers tiered cleanup (safe / cautious / aggressive) with a "BackupMove" mode that copies to a backup folder instead of deleting.

### Layer 6 — Cloud-drive icons (cleans File Explorer)

WPS registers a CLSID `{EEEEFCF7-867B-4FA2-9ABD-884CF531B612}` to show "WPS Cloud Drive" in File Explorer. It appears in:
- "This PC" under NameSpace
- Quick Access (AutomaticDestinations-ms)
- Navigation Pane (HKCU/HKLM CLSID definitions)

⚠ **Common mistake**: the GUID ends in `B612`, not `B610`. Off-by-two char is easy to miss. Verify the actual GUID via `Get-ItemProperty "HKCR:\CLSID\{EEEEFCF7-...}"` before deletion.

To remove: delete the NameSpace reference, then HKCU CLSID definition, then HKLM CLSID definition (the last one requires admin).

## How to use this skill

When invoked, the user wants one of the layers. Ask which one, then run the matching script. Each script is self-contained and idempotent.

### Scripts the skill provides

1. **`enforce-wps-restrictions.ps1`** — runs Layer 1+2+3+4+5 (the common case). Has `-Enforce` / `-Undo` switches.
2. **`disable-wps-autostart.ps1`** — Layer 3 only (registry Run + scheduled tasks). Non-admin-friendly.
3. **`block-wps-firewall.ps1`** — Layer 1 only. Generates `Block WPS - <process>` rules.
4. **`_wps_storage_scan.ps1`** — Layer 5 read-only analysis. Output: top-10 by size per category.
5. **`_wps_cleanup_safe.ps1`** — Layer 5 with `-Mode RecycleBin|BackupMove|HardDelete|DryRun`.
6. **`_wps_cloud_remove_v2.ps1`** — Layer 6 (the correct CLSID). Admin required.

### Default workflow

If the user doesn't specify a layer, run Layer 1+2+3+4 in one shot via `enforce-wps-restrictions.ps1 -Enforce`. Then offer to do Layer 5 and Layer 6 separately.

If the user is unsure, ask:
1. "Which restriction do you want? (block network / kill auto-start / clean space / remove cloud icon / all of the above)"
2. "Do you want to keep this reversible? (default yes)"

## Reversibility

Every action can be undone:
- `enforce-wps-restrictions.ps1 -Undo` reverts all 4 layers
- Firewall rules can be individually `Disable-NetFirewallRule`'d
- Scheduled tasks can be `Enable-ScheduledTask`'d
- Service can be `Set-Service -StartupType Manual`'d
- Cloud-drive cleanup has the WPS installer as ultimate fallback (WPS will re-register on next launch, but you can then re-delete)

## Common pitfalls (the model should know)

1. **PowerShell 5.1 doesn't support inline `if/else` ternary** like `'X' if cond else 'Y'`. Use an `if/else` block assigned to a variable first.
2. **PowerShell scripts without UTF-8 BOM** are read as ANSI, breaking Chinese strings. Always add BOM via `(Get-Content -Raw -Encoding UTF8) | Set-Content -Encoding UTF8 -NoNewline`.
3. **WPS self-heals scheduled tasks** — re-running the disable step is needed after each WPS launch until WPS is also uninstalled.
4. **The CEF subprocess** (`promecefpluginhost.exe`) must be firewall-blocked explicitly; binding only `wps.exe` is bypassed.
5. **The cloud-drive CLSID ends in `B612`**, not `B610`. Use the exact GUID.
6. **`InvokeVerb('delete')`** for moving to Recycle Bin is unreliable in non-interactive shells (it triggers a confirmation dialog). Use `Remove-Item` or `Shell.Application` COM carefully.
7. **When WPS is running**, log files in `office6\log\` are locked. Close WPS first or use `cmd /c rd /s /q` for forced deletion.
8. **Some restrictions require running as Administrator**. Detect via `[Security.Principal.WindowsPrincipal]` and prompt the user.
9. **Don't just delete `addons\`** — it has ~700 MB but breaking individual modules breaks specific WPS features.
10. **The C 盘残留 `C:\Program Files (x86)\Kingsoft\`** is often a leftover after moving WPS to another drive. Usually <1 MB, safe to ignore.

## Script-writing conventions

When extending this skill or writing new restriction scripts:
- Always set `$ErrorActionPreference = "Stop"` for fail-fast
- Use UTF-8 with BOM for any file containing non-ASCII
- Prefer `Shell.Application` COM over `Microsoft.VisualBasic.FileIO` for Recycle Bin (the latter has assembly-load issues on some systems)
- Use `sc.exe config <svc> start= disabled` over `Set-Service` (more portable, XP-compatible)
- Firewall rules should be `Outbound Block`, profile `Any`, bound to absolute program path
- Always provide a `-WhatIf` / dry-run mode
- Log the operation with timestamp to `C:\Users\<user>\wps_cleanup_<timestamp>.log`

## Privacy

This skill does not collect or transmit any data. It only modifies the local system (firewall rules, scheduled tasks, service config, files). No network requests. No telemetry. Safe to run on any machine.
