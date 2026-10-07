# 01 — Local development setup (`tutor dev`)

Goal: the full stack on one machine, with the brand CSS, the MFE header/footer code and the marketing MFEs
reloading without image builds.

## Prerequisites

- Docker, Python 3.12, Node 20+ (Node 24 is what the MFE images use), `uv` or `pip`.
- Tutor 22 (Verawood) with `tutor-mfe` in a virtualenv, e.g. `~/tutor-env-veravood`.
- Clones side by side (names matter for the MFE mounts):

```
workspace/
├── tutor-tels-theme-plugins/          this repo (branch tels-template-improvements/veravood.master)
├── tels-brand-openedx/                branch tels-template-improvements-brand
├── control-panel/                     branch tels-template-improvements
└── mfes/
    ├── frontend-app-template-1/       frontend-app-tels-public @ native-plus-template-a
    └── frontend-app-template-2/       frontend-app-tels-public @ native-plus-template-b
```

The folder of a marketing MFE **must** be `frontend-app-<template id>`: Tutor derives the app name, the dev
image name (`<id>-dev`) and the compose service from it.

## 1. Install and enable the plugin

```bash
source ~/tutor-env-veravood/bin/activate
pip install -e ./tutor-tels-theme-plugins          # editable: plugin.py changes apply on `tutor config save`
tutor plugins enable mfe indigo
```

The marketing MFEs and the landing-page settings (`CATALOG_MICROFRONTEND_URL`, `ENABLE_CATALOG_MICROFRONTEND`)
come from `SITE_TEMPLATES` in `tutorindigo/plugin.py`. Do **not** also register `template-1` / `template-2`
in a standalone `MFE_APPS` plugin.

## 2. Brand package (CSS)

```bash
cd tels-brand-openedx
npm install
make build            # dist/ (shared base) + dist/templates/<id>/ for every template + dist/templates/index.json
npm run serve         # port 3000 — keep it running while you develop
```

`npm run serve` is the "development" brand source: every MFE loads its CSS from `http://localhost:3000`, and
`SiteTemplate.jsx` points the links at `templates/<id>/` of the selected template. After a change to tokens or
SCSS, run `make build` again; a page reload shows it. Without this server the MFEs have no brand CSS.

## 3. Tutor configuration

```bash
tutor config save \
  --set INDIGO_BRAND_THEME_SOURCE=development \
  --set INDIGO_BRAND_THEME_DEVELOPMENT_URL=http://localhost:3000 \
  --set INDIGO_BRAND_THEME_DEVELOPMENT_URL_INTERNAL=http://172.22.0.1:3000 \
  --set INDIGO_BRAND_REPO_REF=tels-template-improvements-brand \
  --set INDIGO_SITE_TEMPLATE_DEFAULT=template-1
```

- `INDIGO_BRAND_THEME_DEVELOPMENT_URL_INTERNAL` is the same server as seen from inside the LMS container, so
  control-panel can read the template manifest and show template names. Find the gateway with
  `docker network inspect tutor_dev_<project>_default --format '{{(index .IPAM.Config 0).Gateway}}'`
  (`tutor_dev_verawood_default` → `172.22.0.1` here). Leave it empty if you do not care about names.
- `INDIGO_BRAND_REPO_REF` is the branch of the `@edx/brand` npm package baked into MFE images (fallback CSS).
- Settings you may want to look at: `INDIGO_ENABLE_DARK_TOGGLE`, `INDIGO_ENABLE_LANGUAGE_MENU`,
  `INDIGO_SUPPORTED_LANGUAGES`, `INDIGO_FOOTER_*`, `INDIGO_HOME_URL` … (`tutor config printvalue <NAME>`).

## 4. control-panel (theme configuration page, site template, landing redirect)

Mount the checkout so the LMS and CMS install it in editable mode:

```bash
tutor mounts add /path/to/workspace/control-panel
```

A one-line plugin tells Tutor that `control-panel` is an `openedx` mount (`~/.local/share/tutor-plugins/tels_extensions_plugin.py`):

```python
from tutor import hooks
hooks.Filters.MOUNTED_DIRECTORIES.add_item(("openedx", "control-panel"))
```

After the containers are **created** (first `tutor dev start`, or any `--force-recreate`) install the editable
package and migrate:

```bash
for c in lms cms; do docker exec tutor_dev_<project>-$c-1 pip install --no-deps --no-build-isolation -e /mnt/control-panel; done
docker exec tutor_dev_<project>-lms-1 ./manage.py lms migrate ui_configuration
```

Python changes reload automatically. The theme page's JavaScript is a built bundle; after editing
`ui_configuration/theme_builder/src/`:

```bash
cd control-panel/ui_configuration/theme_builder && npm ci && npm run build
```

If you ever delete and re-clone the folder, the running containers keep the old (now empty) bind mount:
recreate lms/cms (`tutor dev dc up -d --force-recreate --no-deps lms cms`) and redo the editable installs.

## 5. Marketing MFEs (one dev container per template)

For each template id (`template-1`, `template-2`, …):

1. Clone the branch as `mfes/frontend-app-<id>` and check `.env.development`:
   `PUBLIC_PATH='/public'`, `APP_ID='<id>'`, and **no** `MFE_CONFIG_API_URL` / `PARAGON_THEME_URLS` lines
   (dotenv-webpack would let them override the container environment).
2. Mount the clone and the rendered plugin configuration:
   ```bash
   tutor mounts add /path/to/workspace/mfes/frontend-app-<id>
   tutor mounts add "<id>:$(tutor config printroot)/env/plugins/mfe/build/mfe/env.config.jsx:/openedx/app/env.config.jsx"
   tutor config save
   ```
   The second mount makes the dev container use this plugin's header, footer and `SiteTemplate.jsx` instead of
   the repo's own local copies (the same trick is used for `learning`).
3. Build the dev image once (it bakes `PUBLIC_PATH=/public/` and the brand package) and start it:
   ```bash
   tutor images build <id>-dev
   tutor dev start -d <id>
   ```
   Because the folder is mounted, the image is built from your local clone, not from GitHub.

Any marketing dev server serves `/public/*` for the **selected** template: it proxies to the other template's
dev server when needed (`mfe-webpack-dev-config` patch; it polls the LMS every 5 s). So
`http://apps.local.openedx.io:2024/public/` is the single landing URL in dev too.

## 6. Other MFEs

The `mfe` container serves the image-built MFEs (account, profile, dashboard, catalog, discussions, …). They need
`tutor images build mfe` to pick up plugin component changes. For the Learning MFE, mount it like a marketing MFE
(folder `frontend-app-learning` + the `env.config.jsx` mount) to get live reload.

## 7. Start and verify

```bash
tutor dev start -d
```

| Check | Expected |
|---|---|
| `curl -sI http://local.openedx.io:8000/` | `302` to `http://apps.local.openedx.io:2024/public/` (signed-out) |
| `curl -s http://local.openedx.io:8000/ui_configuration/site-template` | `{"template": "...", "path": "templates/...", ...}` |
| `http://local.openedx.io:8000/theme/ui_configuration/light#site-template` | the templates of `dist/templates/index.json`; Save switches every app on its next page load |
| `http://apps.local.openedx.io:2024/public/` | the selected template's marketing site; header has language menu and dark toggle |
| any MFE page | `<link>`s point at `http://localhost:3000/templates/<id>/…`, header is the template's |

## 8. Daily workflow: what reloads how

| You changed | Do |
|---|---|
| `tutorindigo/plugin.py`, `components/*.jsx`, `patches/*` | `tutor config save`, then `docker restart` the mounted dev containers (learning, template-1, template-2); LMS settings reload by themselves |
| tels-brand-openedx tokens / SCSS | `make build` (port 3000 serves the result); reload the page |
| control-panel Python | nothing (autoreload); migrations: `./manage.py lms migrate ui_configuration` |
| control-panel `theme_builder/src` | `npm run build` in `ui_configuration/theme_builder` |
| a marketing MFE's source | nothing (webpack dev server) |
| `SITE_TEMPLATES` (new marketing MFE) | `tutor config save`, `tutor images build <id>-dev`, `tutor dev start -d <id>` |

## Troubleshooting

- **No CSS on any MFE** — `npm run serve` is not running, or `INDIGO_BRAND_THEME_SOURCE` is `live` and the brand
  branch on GitHub has no `dist/`.
- **Theme page lists ids instead of names** — control-panel cannot reach the manifest; set
  `INDIGO_BRAND_THEME_DEVELOPMENT_URL_INTERNAL` (section 3).
- **`/ui_configuration/...` returns the LMS 404 page** — control-panel is not importable in the container
  (re-clone, recreated container): redo the editable install (section 4).
- **`tutor dev` fails with "mapping key already defined"** — a `local-docker-compose-dev-services` patch
  redefined an MFE service that tutor-mfe already defines; put per-app environment in the Dockerfile instead.
- **`mkdir: cannot create directory 'src/i18n/messages'` during `tutor images build <id>-dev`** — the branch commits
  that folder; its Makefile must use `mkdir -p`.
- **A proxied marketing page does not hot-reload** — reload once; the websocket follows the selected template's
  dev server only for `/ws`.
