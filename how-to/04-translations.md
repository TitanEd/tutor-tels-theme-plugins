# 04 — Translations (Hindi, Arabic, Spanish)

How the marketing site templates, the shared header and footer, and the control-panel APIs are translated,
and how to update a translation or add a string. The source of truth for every translation is TitanEd's fork
of **openedx-translations** (`TitanEd/openedx-translations`, branch `tels/verawood.1`), following
[OEP-58](https://docs.openedx.org/en/latest/developers/references/i18n.html): code holds English only, the
translations repository holds one JSON (MFEs) or `.po` (Django) file per language, and `atlas` pulls them into
the images at build time.

## What is translated and where

| Strings | Source code (English, `defineMessages`) | Resource in `TitanEd/openedx-translations` |
|---|---|---|
| Template-1 pages (home, catalog, course, contact, about, legal) | `frontend-app-tels-public` branch `native-plus-template-a` | `translations/frontend-app-tels-public/` |
| Template-2 pages | `frontend-app-tels-public` branch `native-plus-template-b` | `translations/frontend-app-tels-public-template-2/` |
| Header of every template, language menu, theme switch, user menu, catalog course card | this plugin, `tutorindigo/components/` (`tels.header.*`, `account.user.menu.*`, `generic.*`) | `translations/frontend-component-header/` (TitanEd keys added to the upstream file) |
| Footer of every template | this plugin (`indigo.footer.*`) | `translations/frontend-component-footer/` |
| Contact form, newsletter and catalog API messages, Django admin labels | `control-panel` apps `contat_us`, `newsletter`, `course_metadata` (`gettext`) | `<app>/locale/<lang>/LC_MESSAGES/django.po` + `.mo` in control-panel itself |
| LMS, Studio and the other MFEs | upstream Open edX | upstream resources, pulled from the same fork |

Languages: `hi`, `ar` and `es_419` are complete for everything above. The language menu (`INDIGO_SUPPORTED_LANGUAGES`
in `tutorindigo/plugin.py`) lists en, hi, ar, es-419, fr, pt-pt, zh-cn; French, Portuguese and Chinese only cover
the upstream Open edX strings, so the marketing site falls back to English there.

What is **not** translated by design: catalog data entered by administrators (course titles and descriptions,
organisation names, subject names other than the twelve standard ones, skills, the free-text copyright line of
the footer settings when it differs from the default) and course content.

## How it reaches the site

1. **Build time.** `tutor images build mfe` runs each MFE's `make pull_translations`, which calls
   `atlas pull --repository=TitanEd/openedx-translations --revision=tels/verawood.1 …` (the `ATLAS_REPOSITORY`
   and `ATLAS_REVISION` Tutor settings) and copies the resources listed in the MFE's `Makefile` into
   `src/i18n/messages/<resource>/<lang>.json`; `intl-imports.js` then regenerates `src/i18n/index.js`. The
   plugin's translation safety net (`plugin.py`) also merges the header and footer resources into every styled
   MFE, so the chrome is translated in the learning MFE, the account MFE, etc.
2. **Run time.** frontend-platform reads the `openedx-language-preference` cookie (set by the header's language
   menu for the LMS domain, so the LMS, Studio and every MFE switch together), loads that language's messages,
   and sets `dir="rtl"` for Arabic. The templates also set `<html lang>`.
3. **APIs.** The LMS activates the same cookie's language for API requests sent with credentials, so the
   control-panel responses (validation errors, "Thanks! You're on the list.") come back translated.

`src/i18n/messages/` is git-ignored in both MFE branches and `src/i18n/index.js` is the committed placeholder;
never commit pulled files to the MFE.

## Local development (`tutor dev`)

The dev containers bind-mount the MFE source, so nothing is pulled and every string shows in English until you
pull from your local checkout of the fork:

```bash
# workspace layout: tels_verawood/mfes/<mfe> and tels_verawood/openedx-translations
tutor-tels-theme-plugins/scripts/pull-mfe-translations.sh mfes/frontend-app-template-1
tutor-tels-theme-plugins/scripts/pull-mfe-translations.sh mfes/frontend-app-template-2
```

The script reads the `atlas` mappings of the MFE's `Makefile`, copies the resources from the checkout and
regenerates `src/i18n/index.js`; the running dev server picks the files up. Re-run it after editing a language
file. Leave the regenerated `src/i18n/index.js` out of your commits.

Changes to header or footer components in this plugin reach the dev containers through the generated
`env.config.jsx`: run `tutor config save` and then `tutor dev start -d template-1 template-2` (the file is
bind-mounted, so a restart is needed, not an image build).

To test a language in the browser, pick it in the header's language menu, or set the cookie
`openedx-language-preference=hi` (`ar`, `es-419`) for the domain `local.openedx.io`.

## Add or change a string

1. Add it with `defineMessages` (never a literal in JSX; data that is an English key, such as
   `'Available now'` or `'Introductory'`, is mapped to a message by the taxonomy helpers before it is shown).
   Keep ids unique across templates: two components must not share an id with different English text
   (template-2's footer uses `indigo.footer.link.termsOfUse`, template-1's `indigo.footer.link.terms`).
2. Extract the English strings:
   - template branch: `cd mfes/frontend-app-template-2 && make extract_translations`
     (writes `src/i18n/transifex_input.json`, git-ignored);
   - plugin components: `mfes/frontend-app-template-1/node_modules/.bin/formatjs extract 'tutor-tels-theme-plugins/tutorindigo/components/*.jsx' --out-file /tmp/plugin.json`.
3. Sync the resource in the fork and see what is missing per language:
   ```bash
   cd openedx-translations
   python scripts/tels_sync_mfe_resource.py translations/frontend-app-tels-public-template-2 ../mfes/frontend-app-template-2/src/i18n/transifex_input.json
   python scripts/tels_sync_mfe_resource.py translations/frontend-component-header /tmp/plugin.json --merge
   python scripts/tels_sync_mfe_resource.py translations/frontend-component-footer /tmp/plugin.json --merge
   ```
   Without `--merge` the script removes keys that left the source from the English file and from every
   language; with `--merge` (shared header and footer resources, whose upstream keys are not in the extracted
   file) it only adds and updates. A key whose English text changed loses its old translations.
4. Translate the missing keys in `translations/<resource>/src/i18n/messages/{hi,ar,es_419}.json`. Keep ICU
   placeholders (`{siteName}`, `{count, plural, …}`) exactly; Arabic plurals use the six CLDR categories.
5. Validate (`make validate_translation_files` in the fork, or any JSON linter), pull locally (above), check in
   the browser, commit and push the fork, then rebuild: `tutor images build mfe`.

### Control-panel (Django) strings

```bash
# extract (inside the LMS container, from the app directory)
docker exec -w /mnt/control-panel/newsletter tutor_dev_verawood-lms-1 \
  django-admin makemessages -l hi -l ar -l es_419 --no-location --no-wrap
# translate <app>/locale/<lang>/LC_MESSAGES/django.po, then compile
docker exec -w /mnt/control-panel/newsletter tutor_dev_verawood-lms-1 django-admin compilemessages
```

Each app carries its own `locale/` directory (Django finds it through the installed app, so `LOCALE_PATHS`, a
Tutor `Derived` setting, is never touched). The compiled `.mo` files are committed (`.gitignore` allows
`**/locale/**/*.mo`) and shipped by `MANIFEST.in`, because the production image installs control-panel from git
without a build step. A new `.mo` reaches production with `tutor images build openedx`.

## Add a language

1. Add it to `INDIGO_SUPPORTED_LANGUAGES` in `tutorindigo/plugin.py` (`value` is the Open edX language code,
   lower case, e.g. `pt-br`); `tutor config save`.
2. Release it in the LMS: Django admin → Dark Lang → "Released languages" (dev has `ar,hi,es-419`).
3. Create or fill `messages/<code>.json` (atlas file names use `_`: `pt_BR.json`) in the four TitanEd
   resources and the control-panel `.po` files, as above.
