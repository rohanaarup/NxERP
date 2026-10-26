# NXERP — Agent Handoff Checkpoint

**Purpose:** Durable checkpoint so another agent can resume without repeating the investigation. Updated after each meaningful stage.

**Workspace root:** `C:\Users\darla\OneDrive\Desktop\NXERP CORE`
**Working tree:** `frapper sria/nxerp-integration/` (the integration / target repository)

---

## Phase 0 — Recovery (VERIFIED)

### Git repositories found
| Path | Remote | Branch | Commit | State |
|------|--------|--------|--------|-------|
| `C:\Users\darla\OneDrive\Desktop\NXERP CORE` (root) | none | `main` | none (no commits) | Empty wrapper; `frapper sria/` untracked |
| `.../frapper sria/helpdesk` | `origin`=frappe/helpdesk, `company`=Sriainfotech/Frappe-Help-Desk | `feature/nxerp-login-page` | `1c6981cc5` | 51 changed files (40 modified + 11 untracked) — **preserved, not touched** |
| `.../frapper sria/nxerp-integration` (TARGET) | `origin`=Sria-Infotech-Pvt-Ltd/NxERP.git, `rohanaarup`=rohanaarup/NxERP.git | `codex/nxerp-integration` | `07a5b85` | Working tree **clean**, up to date with remote |
| `.../nxerp-integration/erpnext-source` | frappe/erpnext | detached | `ade850bbd6` (v16.52.1) | Local inspection clone, git-ignored |
| `.../nxerp-integration/frappe-source` | frappe/frappe | detached | `e8d41dd` (v16.53.0) | Local inspection clone, git-ignored |

### Root repo git user
`user.name=rohanaarup`, `user.email=rudraarupa22@gmail.com`. No commits yet.

### Authentication / access (from implementation log + inspection)
- Destination `Sria-Infotech-Pvt-Ltd/NxERP`: account `rohanaarup` reported `push: false`; no commit pushed. GitHub API returned 404 for branch protection. **Not verified whether push is possible.**

---

## Phase 1 — ERPNext / Frappe source (VERIFIED)

`erpnext-source/` and `frappe-source/` already exist inside `nxerp-integration/` (no need to re-clone).

| Project | Ref | Commit | Declared compatibility |
|---------|-----|--------|------------------------|
| Frappe | `v16.53.0` | `e8d41dd0061a32ee781caefe7d0b0d2bb7c15362` | satisfies ERPNext `>=16.50.0,<17.0.0` |
| ERPNext | `v16.52.1` | `ade850bbd6a7412e9994a9637d2c5c713771632a` | Python `>=3.14` |
| Telephony | `develop` (pin) | `9447577500a25d242088398157b72c654fa34b20` | required by helpdesk |

These are **source-metadata compatible**, not a validated installation. No full Frappe Bench exists locally (Windows, no MariaDB/Redis/WSL).

---

## Phase 2 — Repository architecture (VERIFIED)

Target repo = `nxerp-integration` (origin `https://github.com/Sria-Infotech-Pvt-Ltd/NxERP.git`).

Layout:
```
nxerp-integration/
├── apps/
│   ├── helpdesk/     <- customized Frappe Helpdesk snapshot (copied from helpdesk repo @ 1c6981cc5, incl. uncommitted theme/login changes)
│   ├── nxerp/        <- NXERP branding app (login, desk theme, logo, favicon)
│   ├── frappe/       <- only `ui/` subdir present (incomplete local copy; CI fetches frappe from upstream)
│   ├── erpnext/      <- not present locally (CI fetches from upstream)
│   └── telephony/    <- not present locally (CI fetches from upstream)
├── erpnext-source/   <- inspection clone (git-ignored)
├── frappe-source/    <- inspection clone (git-ignored)
├── .github/workflows/{ci,security,cd-staging,release}.yml
├── .github/{CODEOWNERS,PULL_REQUEST_TEMPLATE.md,ISSUE_TEMPLATE/}
├── docs/{architecture,branching,deployment,migration,onboarding,source-pins}.md
├── README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, CHANGELOG.md
├── .editorconfig, .gitignore, .env.example, pyproject.toml
```

`apps/frappe/` is incomplete (`ui/` only) — CI re-checks upstream refs into temporary `apps/` paths; the vendored `erpnext-source/`/`frappe-source/` are git-ignored inspection material, not the install source.

### NXERP app (`apps/nxerp/`)
- `nxerp/hooks.py`: `required_apps=["erpnext","helpdesk"]`, `app_include_css="/assets/nxerp/css/nxerp-desk-theme.css"`, `after_install="nxerp.branding.apply_branding"`, `app_logo_url`, `website_context` favicon/splash.
- `nxerp/branding.py`: `apply_branding()` sets Website Settings app_name, HD Settings brand_name/logo/favicon; idempotent.
- `nxerp/www/login.html`: **canonical /login**; extends `frappe/www/login.html` (auth 100% Frappe), adds NXERP layout + CSS.
- `nxerp/www/login.py`: calls `frappe.www.login.get_context`, only layers branding context; drops `login_with_frappe_cloud_url`.
- `nxerp/public/css/{nxerp-theme,nxerp-login,nxerp-desk-theme}.css`, `public/images/`, `public/fonts/`.
- `nxerp/pyproject.toml`: `frappe >=16.50.0,<17.0.0`.

### Helpdesk app (`apps/helpdesk/`)
- `helpdesk/hooks.py`: `required_apps=["telephony"]`, `auth_hooks=["helpdesk.auth.authenticate"]`, `add_to_apps_screen` route `/helpdesk`, `doc_events` ERPNext sync, `permission_query_conditions`, `has_permission`, `website_route_rules`, `before_tests`, `after_install`, `after_migrate`.
- `helpdesk/auth.py` present (auth hook / endpoint allowlist).
- `helpdesk/integrations/erpnext/` present (customer, user_permission, doc_share, mirror_sync, api, utils).
- `helpdesk/patches.txt` present.
- `helpdesk/www/` under the package exists (portal `index.py`) but **no `helpdesk/www/login.html`/`login.py`** — so no competing /login route from Helpdesk.

### Login / auth architecture (Phase 4 — VERIFIED as implemented)
- Canonical /login = `apps/nxerp/www/login.py`+`login.html`; extends Frappe's own `get_context`, so login/forgot-password/email-link/2FA/social/redirect are Frappe's code. No duplicate password DB, no separate agent login.
- Old Helpdesk login preserved for reference at `apps/helpdesk/legacy_reference/login.html`+`login.py` (outside `www/`, not routable).
- No conflicting Helpdesk internal-user login path active in the snapshot.
- Customer portal routes remain in Helpdesk (`website_route_rules /helpdesk/<path>`).

---

## Phase 3 — Helpdesk integration (VERIFIED as snapshotted)

`apps/helpdesk/` is a snapshot of the helpdesk repo at `1c6981cc5` (`feature/nxerp-login-page`), including pre-existing uncommitted theme/login/UI changes. The source helpdesk repo is untouched. DocTypes use `HD_` prefix (HD Ticket, HD Ticket Activity, HD Ticket Status/Priority/Type, HD Agent, HD Team, HD Customer, HD SLA, HD Settings, HD Article/Category, HD Saved Reply).

---

## Verified checks (PASS — executed locally)

| Check | Command | Result |
|-------|---------|--------|
| Python compileall | `python -m compileall apps/helpdesk/helpdesk apps/nxerp/nxerp` | **PASS** (exit 0) |
| Flake8 strict | `python -m flake8 --config apps/helpdesk/.github/helpers/.flake8_strict apps/helpdesk/helpdesk apps/nxerp/nxerp` | **PASS** (exit 0) |
| Workflow YAML parse | `yaml.safe_load` on all 4 `.github/workflows/*.yml` | **PASS** (all parse) |
| Theme check | `yarn theme:check` (in apps/helpdesk/desk) | **PASS** — generated files up to date, 384 frappe-ui tokens/mode, 99 light/dark contrast passed, synced copies up to date |
| Theme audit | `yarn theme:audit` | **PASS** — no hardcoded colors outside allowlist |
| Secret scan (grep) | scanned `apps/**/*.py` for sk_/AKIA/password=/secret= | **PASS** — only synthetic test data (`mail-key`/`mail-secret` in a test) |

Toolchain available locally: Python 3.14.3, Node v24.18.0, npm 11.16.0, yarn 1.22.22, git 2.47.1.

---

## NOT VERIFIED (environment limitations)

| Check | Reason |
|-------|--------|
| `yarn build` (Vite) | Hangs/no output after 5 min on Windows — must run on Linux CI runner |
| Full Bench install + `bench migrate` | No MariaDB, Redis, frappe-bench, WSL/Docker on this Windows session |
| Server tests (`bench run-tests --app helpdesk`) | No Bench / database available |
| Login/logout/portal/ERPNext workflow E2E | No running site |
| GitHub Actions execution | Workflows not run on GitHub yet |
| Staging / production deploy | No staging infrastructure or credentials verified |
| Branch protection / required reviews | API 404; not configured |
| `git push` to `Sria-Infotech-Pvt-Ltd/NxERP` | Account reported `push: false` — not yet tested |

---

## Outstanding work

1. **Create/push integration commit** — current tree is clean on `codex/nxerp-integration`; the implemented files are already committed (`07a5b85`). No uncommitted changes pending in `nxerp-integration`.
2. **Attempt `git push`** to `origin` (`Sria-Infotech-Pvt-Ltd/NxERP`) — verify write access; if `push: false`, document and request admin intervention.
3. **Configure branch protection** on `main` (per `docs/branching.md`) — requires org admin; document exact steps if not permitted.
4. **Run CI on GitHub** (Linux) — `yarn build`, server tests, security scans.
5. **Validate on a real Bench** — install ERPNext v16.52.1 + Frappe v16.53.0 + telephony + helpdesk + nxerp; verify login, helpdesk workflows, migrations.
6. **CODEOWNERS** — currently a placeholder (no real usernames/teams); add actual organization accounts.

---

## Architectural decisions

- **Monorepo distribution repo:** `nxerp-integration` contains the two company apps (`helpdesk`, `nxerp`); upstream Frappe/ERPNext/Telephony are pinned and fetched by CI/Bench, not vendored as installable Python packages (avoids copying Helpdesk into ERPNext's internal package).
- **Version pins:** Frappe `v16.53.0`, ERPNext `v16.52.1`, Telephony pin `94475775`. Documented in `docs/source-pins.md` and `docs/architecture.md`.
- **Login unification:** NXERP app owns `/login` (installed last, extends Frappe's login); Helpdesk's old login moved to `legacy_reference/` (not routable); single Frappe session across Desk + Helpdesk.
- **No destructive migrations:** patches are idempotent; `bench migrate` only; no raw DDL.
- **Do not force-push; preserve remote history.**

---

## Current phase / next action

**Phases 0-9 complete locally.** All feasible checks executed (see verified PASS list above).

### Push result (Phase 10) — BLOCKED by permissions
`git push origin main` → `remote: Permission to Sria-Infotech-Pvt-Ltd/NxERP.git denied to rohanaarup.` HTTP 403. The authenticated identity `rohanaarup` has **no write access** to `Sria-Infotech-Pvt-Ltd/NxERP.git`. The push did NOT succeed and was not forced. Local `main` is at `37531b7` (ahead of `origin/main` = `c80531a` "Initial commit").

### Precise remaining action (requires human intervention)
1. An organization administrator must grant write access to `Sria-Infotech-Pvt-Ltd/NxERP.git` for an authenticated identity (e.g. add `rohanaarup` to the repo with write/triage, or use a deploy key / bot token with `contents: write`).
2. After access is granted, run: `git push origin main` from `nxerp-integration` (branch `main`, commit `37531b7`). This is a fast-forward over `origin/main` (`c80531a`); no force-push needed.
3. Configure branch protection on `main` per `docs/branching.md` (requires admin/repo write).
4. Run CI on GitHub (Linux runner) to execute `yarn build` + server tests + security scans (not runnable on this Windows session).
5. Validate on a real Frappe Bench (Frappe v16.53.0 + ERPNext v16.52.1 + telephony + helpdesk + nxerp).
