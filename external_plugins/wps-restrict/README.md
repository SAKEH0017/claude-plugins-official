# wps-restrict

A Claude Code skill that helps Windows users restrict WPS Office — block its network access, stop background activity, prevent auto-start, remove cloud-drive icons from File Explorer, and reclaim disk space.

## What it does

WPS Office is a popular free office suite, but it ships with:

- Background services that re-enable themselves when disabled
- An embedded Chromium component (CEF) that can bypass main-process firewall rules
- Scheduled tasks that auto-launch WPS on login
- A Windows service (`wpscloudsvr`) that calls home
- A cloud drive that injects icons into File Explorer
- Gigabytes of accumulated cache, logs, and plugin versions

Single-point fixes don't work because WPS self-heals. This skill applies **defense in depth**: six independent layers, each reversible. If one layer fails (e.g., WPS re-enables a scheduled task), the others still hold.

## Core layers

1. **Firewall** — Outbound block for 7 WPS executables including the CEF subprocess
2. **Configuration** — Set 8 `Enable*=0` switches in WPS's INI files (kills ads, recommendations, cloud, updates)
3. **Scheduled tasks** — Disable 3 WPS auto-launch tasks
4. **Service** — Disable `wpscloudsvr` Windows service
5. **Disk cleanup** — Tiered reclaim of WPS cache, logs, plugin pools (read-only analysis first)
6. **Cloud-drive icons** — Remove WPS cloud CLSID from File Explorer

## What you keep

- Local document editing (.docx, .xlsx, .pptx) — works fully
- File association with WPS for double-click opening (we don't change it)
- No impact on Microsoft Office

## Installation

### From Claude Code

```
/plugin install wps-restrict
```

### Manual installation

Copy `skills/wps-restrict/SKILL.md` to `~/.claude/skills/wps-restrict/SKILL.md` on Windows.

## Usage

After installation, simply ask Claude Code any of:

- "限制 WPS" / "Restrict WPS"
- "防止 WPS 自启动" / "Stop WPS from auto-starting"
- "阻止 WPS 联网" / "Block WPS network access"
- "删除 WPS 云盘图标" / "Remove WPS cloud-drive icon"
- "清理 WPS 占用的空间" / "Clean WPS disk space"
- "WPS 弹广告" / "WPS popups"
- "wpscloudsvr 在后台跑" / "WPS background service"

The skill detects the current PowerShell session and prompts for elevation when needed (most restriction steps require administrator).

## Reversibility

Every action can be undone:

```powershell
# Revert everything (firewall + tasks + service + config)
wps-restrict enforce --undo

# Or individually
Remove-NetFirewallRule -DisplayName "Block WPS - *"
Enable-ScheduledTask -TaskName "WpsUpdateLogonTask_*"
Set-Service wpscloudsvr -StartupType Manual
```

## Permissions required

- **Non-admin**: writing WPS config INI files, deleting Quick Access history
- **Administrator**: creating firewall rules, disabling scheduled tasks, disabling the `wpscloudsvr` service, deleting HKLM CLSID entries

The skill detects elevation status and prompts the user to re-run in an elevated PowerShell when needed.

## Privacy

This skill does not collect or transmit any data. It only modifies the local Windows system (firewall rules, scheduled tasks, service config, files). No network requests. No telemetry. Safe to run on any machine.

## Known pitfalls (lessons from real use)

The skill's `SKILL.md` documents 10 common pitfalls future Claude instances should know about, including:

- PowerShell 5.1 doesn't support inline `if/else` ternary expressions
- PowerShell scripts need UTF-8 BOM or Chinese strings get corrupted
- WPS's CEF subprocess (`promecefpluginhost.exe`) needs separate firewall blocking
- WPS's cloud-drive CLSID ends in `B612`, not `B610` (off-by-two is easy to miss)
- WPS self-heals scheduled tasks when launched — re-run disable after each WPS launch
- `InvokeVerb('delete')` for Recycle Bin is unreliable in non-interactive shells

## License

MIT — see `LICENSE`.
