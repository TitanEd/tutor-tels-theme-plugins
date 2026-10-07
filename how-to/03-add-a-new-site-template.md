# 03 — Add a new site template

Example: `template-3`. A template id must match `[a-z0-9][a-z0-9-]*` and is used **unchanged** in four places:
the marketing MFE branch (as `APP_ID`), the brand layer folder, the plugin registries and `SITE_TEMPLATES`.

## Checklist

| # | Repository | What |
|---|---|---|
| 1 | frontend-app-tels-public | branch `native-plus-template-c`: the marketing MFE (landing, catalog, about, contact, legal pages) |
| 2 | tels-brand-openedx | `paragon/templates/template-3/`: tokens, SCSS, fonts, assets → `dist/templates/template-3/` |
| 3 | tutor-tels-theme-plugins | `Template3Header.jsx`, `Template3Footer.jsx`, registry entries, `SITE_TEMPLATES` entry |
| 4 | tutor / images | dev: `tutor images build template-3-dev`; prod: `tutor images build mfe` |

control-panel needs no change: it lists whatever `dist/templates/index.json` publishes.

## 1. Marketing MFE — `TitanEd/frontend-app-tels-public`

Create the branch from the most recent `native-plus-template-*` branch (keep the shared plumbing, replace pages
and styles):

Keep as is:

- `src/plugin-slots/HeaderSlot` (`org.openedx.frontend.layout.header.v1`) and the footer slot
  (`org.openedx.frontend.layout.footer.v1`): the plugin inserts `SiteHeader` / `SiteFooter` there.
- `src/plugin-slots/publicUrls.js` with `PUBLIC_MFE_MOUNT = '/public'` and `isMarketingMfe`,
  `src/plugin-slots/localIndigoConfig.js`, `ChromeLink.jsx` (in-app links).
- The local `TelsHeader.jsx` / `IndigoFooter.jsx` copies are only for a standalone `npm start`; the Tutor
  configuration replaces them.
- `Makefile`: `pull_translations` must use `mkdir -p src/i18n/messages` (the branch commits that folder).

Set:

- `.env.development`: `PUBLIC_PATH='/public'`, `APP_ID='template-3'`, and **no** `MFE_CONFIG_API_URL` or
  `PARAGON_THEME_URLS` lines.
- Page styles: use design tokens (`var(--pgn-...)`) only, and class names scoped to this template
  (for example `.tels3-*` or your own prefix) so they cannot collide with other templates' pages in the brand repo.
- Translations: `src/i18n/messages/*.json` and `defineMessages` ids; the plugin's translation safety net
  fills header/footer strings at image build.

Push the branch. Note the dev port you will give it (unused: 2024 and 2026 are taken).

## 2. Brand layer — `TitanEd/tels-brand-openedx`

```
paragon/templates/template-3/
├── template.json
├── tokens/                      optional: JSON files mirroring paragon/tokens/src/…
├── _template.scss               the entry
├── _header.scss  _footer.scss  _public.scss   the chrome and the marketing pages
├── overrides/…                   optional Paragon component bridges that differ from the base
├── fonts/                        optional self-hosted fonts (@font-face in _fonts.scss, url("./fonts/…"))
└── assets/                       optional images (url("./assets/…"))
```

`template.json`:

```json
{
  "id": "template-3",
  "name": "Template 3 — <design name>",
  "description": "What it looks like; marketing MFE: frontend-app-tels-public@native-plus-template-c, served at /public.",
  "default": false
}
```

Rules:

- **Tokens**: a file in `tokens/` is deep-merged over the base file with the same relative path. List only what
  changes (for example `themes/light/global/color.json` with `color.primary.base`). A token you give a `$value`
  loses the base token's `modify` (colour mix), so set your own `modify` when you need one. Dark mode: give every
  changed light token a dark twin in `tokens/themes/dark/...`.
- **SCSS**: `_template.scss` is compiled after `paragon/_overrides.scss`, so its rules win over the shared base
  but never meet another template's chrome (each template gets its own `dist/templates/<id>/`). Import order
  that works: fonts → overrides → header → footer → public. Values only through `var(--pgn-*)`; use
  `--pgn-color-text-inverse` for white-on-colour, never literals.
- The header component's classes must match these styles (`.tels-header*` and `.tels-btn*` are what the
  existing headers use; pick your own and style them here).

Build, check and publish:

```bash
make build                                   # also runs scripts/build-template.js for every template
ls dist/templates/template-3/                # core/light/dark(.min).css, theme-urls.json, fonts/, assets/
cat dist/templates/index.json                # the manifest control-panel lists
git add paragon/templates/template-3 dist && git commit && git push
```

Only one template may have `"default": true`.

## 3. Header and footer — `tutor-tels-theme-plugins`

1. Add `tutorindigo/components/Template3Header.jsx` and `Template3Footer.jsx`. All component files are
   concatenated into one `env.config.jsx` module, so every top-level identifier must be unique: prefix them
   (`Template3Header`, `template3HeaderMessages`, `TEMPLATE3_…`). Available in scope: everything in
   `Imports.jsx` (React hooks, `getConfig`, `useIntl`/`defineMessages`, Paragon, FontAwesome icons — add new
   icons there), the helpers of `publicUrls.js` (`resolvePublicMfeUrl`, `publicHomeHref`, `publicCoursesHref`,
   `isMarketingMfe`, `isPublicMfeNavActive`), `HeaderControls` (language menu + dark toggle), and
   `useSiteTemplate()`. Read footer content the same way `Template2Footer` does (`INDIGO_FOOTER_*` with the
   theme page's `FOOTER_CONFIG_URL` taking precedence).
2. Register them:
   ```js
   // SiteHeader.jsx                          // SiteFooter.jsx
   const SITE_TEMPLATE_HEADERS = {            const SITE_TEMPLATE_FOOTERS = {
     'template-1': CustomHeader,                'template-1': IndigoFooter,
     'template-2': Template2Header,             'template-2': Template2Footer,
     'template-3': Template3Header,             'template-3': Template3Footer,
   };                                         };
   ```
3. Add the files to `tutorindigo/patches/mfe-env-config-runtime-definitions`, after `publicUrls.js` /
   `HeaderControls.jsx` and **before** `SiteHeader.jsx` / `SiteFooter.jsx`.
4. Register the template and its marketing MFE in `tutorindigo/plugin.py`:
   ```python
   SITE_TEMPLATES = {
       ...
       "template-3": {
           "repository": "https://github.com/TitanEd/frontend-app-tels-public.git",
           "version": "native-plus-template-c",
           "port": 2028,   # unique dev port
       },
   }
   ```
   Everything else derives from it: the tutor-mfe app, brand package and FontAwesome install, header/footer slots,
   `PUBLIC_PATH=/public/`, the `/public/_t/template-3/` Caddy handler and dispatcher entry, the dev proxy,
   `INDIGO_SITE_TEMPLATES` and `TELS_SITE_TEMPLATES`.
5. Add a `changelog.d/` fragment and a line in `README.rst`.

## 4. Build and run

Local (guide 01, section 5):

```bash
git clone -b native-plus-template-c https://github.com/TitanEd/frontend-app-tels-public.git mfes/frontend-app-template-3
tutor mounts add /path/to/mfes/frontend-app-template-3
tutor mounts add "template-3:$(tutor config printroot)/env/plugins/mfe/build/mfe/env.config.jsx:/openedx/app/env.config.jsx"
tutor config save
tutor images build template-3-dev
tutor dev start -d template-3
docker restart tutor_dev_<project>-learning-1 tutor_dev_<project>-template-1-1 tutor_dev_<project>-template-2-1   # new env.config
```

Production (guide 02): push the plugin branch, `pip install` it on the host, `tutor config save`,
`tutor images build mfe`, redeploy.

## 5. Verify

1. `http(s)://<LMS_HOST>/theme/ui_configuration/light#site-template` lists "Template 3 — …" (from the manifest;
   with the development brand source the LMS must reach the theme server, see guide 01 section 3).
2. Select it and save. On the next page load of any MFE: header and footer are `Template3Header/Footer`, the
   stylesheet links end in `templates/template-3/…`, colours and fonts are yours, no console errors.
3. `/public/` shows the new marketing site; its links stay under `/public/`.
4. Switch back to another template: everything reverts without a restart.

## Gotchas

- Same id everywhere; `APP_ID` in the clone must be the template id, `PUBLIC_PATH` must be `/public`.
- Dev images bake `PUBLIC_PATH`: rebuild `<id>-dev` after adding a template; the `mfe` image needs a rebuild
  for the production dispatcher to know the new id.
- Do not add a `local-docker-compose-dev-services` patch for an MFE service: tutor-mfe already defines it and the
  duplicate key breaks `tutor dev`.
- A brand validation failure on `make build` is about the shared base (`dist/`); template builds print their
  own warnings (for example contrast) without failing the build. Fix them anyway.
- Never put hard-coded colours in template SCSS: dark mode comes from the tokens.
