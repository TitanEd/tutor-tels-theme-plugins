# 02 — Production setup (`tutor local` / Kubernetes)

Goal: the same stack on a server, with the brand CSS served by control-panel ("live" source), one landing URL
(`https://<MFE_HOST>/public`) and template switching from the theme configuration page without redeploys.

## 1. Repositories and branches

| Repository | Branch | Used by |
|---|---|---|
| `TitanEd/tutor-tels-theme-plugins` | `tels-template-improvements/veravood.master` | `pip install` on the Tutor host |
| `TitanEd/tels-brand-openedx` | `tels-template-improvements-brand` | `@edx/brand` npm package in the MFE images (`INDIGO_BRAND_REPO_REF`) **and** the live CSS read by control-panel from the committed `dist/` (`INDIGO_BRAND_THEME_DEPLOYED_URL`) |
| `TitanEd/control-panel` | `tels-template-improvements` | pip-installed into the `openedx` image (`INDIGO_CONTROL_PANEL_REPO_REF`) |
| `TitanEd/frontend-app-tels-public` | `native-plus-template-a`, `native-plus-template-b` | the marketing MFEs, cloned at image build from `SITE_TEMPLATES` |

The brand repository **commits its `dist/`**: after `make build`, push `dist/` too, including
`dist/templates/<id>/` and `dist/templates/index.json`. control-panel reads them from
`https://raw.githubusercontent.com/<repo>/refs/heads/<ref>/dist`.

## 2. Install the plugin

```bash
pip install "git+https://github.com/TitanEd/tutor-tels-theme-plugins.git@tels-template-improvements/veravood.master"
tutor plugins enable mfe indigo
```

Remove any standalone `MFE_APPS` plugin entry for `public` / `template-*` and any `CATALOG_MICROFRONTEND_URL`
patch: `SITE_TEMPLATES` in the plugin provides both.

## 3. Configuration

```bash
tutor config save \
  --set INDIGO_BRAND_THEME_SOURCE=live \
  --set INDIGO_BRAND_REPO=TitanEd/tels-brand-openedx \
  --set INDIGO_BRAND_REPO_REF=tels-template-improvements-brand \
  --set INDIGO_SITE_TEMPLATE_DEFAULT=template-1 \
  --set INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT=true \
  --set INDIGO_CONTROL_PANEL_REPO_REF=tels-template-improvements \
  --set INDIGO_CONTROL_PANEL_REPO_TOKEN=<fine-grained read-only GitHub token for TitanEd/control-panel>
```

| Setting | Meaning |
|---|---|
| `INDIGO_BRAND_THEME_SOURCE` | `live` (recommended): MFEs load `/ui_configuration/theme/{core,light,dark}.min.css` from the LMS; control-panel merges the selected template's build from GitHub with the design tokens saved on the theme page. `deployed`: the raw GitHub `dist/` URLs, template switching of CSS done in the browser by `SiteTemplate.jsx`, no saved tokens. `development`: see guide 01. |
| `INDIGO_BRAND_THEME_DEPLOYED_URL` | Derived from repo + ref; override only for a CDN copy of `dist/`. |
| `INDIGO_SITE_TEMPLATE_DEFAULT` | Template used before an administrator picks one, and `CATALOG_MICROFRONTEND_URL`'s target. |
| `INDIGO_CONTROL_PANEL_REPO_TOKEN` | Read-only token, scoped to the control-panel repository; stored in `config.yml` only. Alternative: mount a checkout (`tutor mounts add /path/control-panel`) or `INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT=false` and install it another way. |
| `INDIGO_ENABLE_DARK_TOGGLE`, `INDIGO_ENABLE_LANGUAGE_MENU`, `INDIGO_SUPPORTED_LANGUAGES` | Header controls. |
| `INDIGO_FOOTER_EXPLORE_LINKS` / `COMPANY` / `SUPPORT`, `INDIGO_FOOTER_CONTACT`, `INDIGO_FOOTER_SOCIAL_LINKS` | Footer defaults; the theme page's Footer settings take precedence for address, email, social links and copyright. |
| `INDIGO_HOME_URL` … `INDIGO_TERMS_URL` | `/public/...` by default; change only if the marketing MFE is mounted elsewhere. |
| `ENABLE_WEB_PROXY` | Must stay `true` (Caddy in front of the MFEs): marketing origins are then relative, so links and the landing redirect stay on `MFE_HOST`. |

## 4. Build the images

```bash
tutor images build openedx     # installs control-panel (ui_configuration) into LMS/CMS
tutor images build mfe         # every MFE + the marketing MFEs + the /public dispatcher (Caddyfile patch)
```

What the `mfe` build does for templates: clones each marketing MFE from `SITE_TEMPLATES`, builds it with
`PUBLIC_PATH=/public/` and assets under `/public/_t/<id>/`, installs the brand package and FontAwesome in every
styled MFE, applies the translation safety net, and renders the Caddyfile that serves `/public/*` through the
dispatcher page.

## 5. Deploy and initialise

```bash
tutor local launch              # or: tutor local start -d && tutor local do init
tutor local run lms ./manage.py lms migrate ui_configuration   # if init did not run migrations
```

## 6. Operate

- **Theme page**: `https://<LMS_HOST>/theme/ui_configuration/light` (staff with the theme permission or
  superusers). `#site-template` lists the templates published in `dist/templates/index.json`; **Save**
  switches, for every app on its next page load: header and footer components, stylesheets, the marketing
  site behind `/public`, and the LMS landing redirect.
- **Propagation**: control-panel caches the upstream CSS and manifest for 60 s (`UI_CONFIGURATION_UPSTREAM_CACHE_SECONDS`)
  and clears them on Save. Browsers keep the `tels-site-template` cookie (90 days, refreshed on every load) only
  as a hint; the LMS answer wins.
- **Landing**: `/` and `/courses` on the LMS answer `302` to `https://<MFE_HOST>/public/...` (signed-in users
  still go to the dashboard, as upstream does). The platform's own `CATALOG_MICROFRONTEND_URL` is the same URL.
- **Brand release**: `make build` in tels-brand-openedx, commit `dist/`, push the branch. Live mode shows it
  within a minute; the npm fallback package inside images updates on the next `tutor images build mfe`.

## 7. When is an image rebuild needed?

| Change | `tutor images build` |
|---|---|
| Admin switches template, edits footer settings or design tokens | none |
| Brand tokens / SCSS (live or deployed source) | none (push `dist/`) |
| Header / footer components, `SiteTemplate.jsx`, `publicUrls.js`, `SITE_TEMPLATES`, Caddy / webpack patches | `mfe` |
| control-panel code | `openedx` |
| Plugin settings (`tutor config save --set …`) | usually none; `openedx`/`mfe` only if a setting is baked at build (brand ref, repo tokens) |

## 8. Security notes

- Public, unauthenticated endpoints served by control-panel: `/ui_configuration/site-template`,
  `/ui_configuration/footer-config`, `/ui_configuration/theme/*` (CSS, fonts, logos). They carry only what the
  pages show; CORS `*` is required because the MFEs are on another host.
- Writes go through `/theme/ui_configuration/api/*` with CSRF protection and the `can_manage_theme` check.
- Keep `INDIGO_CONTROL_PANEL_REPO_TOKEN` out of git and CI logs; rotate it like any deploy key.
- The dispatcher page and the dev proxy only ever load templates listed in `SITE_TEMPLATES`; a cookie with an
  unknown id falls back to the default template.

## 9. Verification checklist

```bash
curl -sI https://<LMS_HOST>/ | grep -i "^location"                      # .../public/
curl -s  https://<LMS_HOST>/ui_configuration/site-template               # selected template + path
curl -sI https://<LMS_HOST>/ui_configuration/theme/light.min.css          # 200 text/css
curl -sI https://<MFE_HOST>/public/                                       # 200 text/html (dispatcher)
curl -sI https://<MFE_HOST>/public/_t/template-1/index.html              # 200 (each template's build)
```

Then, in a browser: open `/public/`, switch the template on the theme page, reload — header, footer, colours,
fonts and the marketing pages change; the URL stays `/public/`.
