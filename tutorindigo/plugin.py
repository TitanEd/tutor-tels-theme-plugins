from __future__ import annotations

import json
import os
import typing as t
from glob import glob

import importlib_resources
from tutor import hooks
from tutor.__about__ import __version_suffix__

from .__about__ import __version__

# Handle version suffix in main mode, just like tutor core
if __version_suffix__:
    __version__ += "-" + __version_suffix__


################# Configuration
config: t.Dict[str, t.Dict[str, t.Any]] = {
    # Add here your new settings
    "defaults": {
        "VERSION": __version__,
        "WELCOME_MESSAGE": "The place for all your online learning",
        "PRIMARY_COLOR": "#15376D",  # Indigo
        "ENABLE_DARK_TOGGLE": True,
        # Footer links are dictionaries with a "title" and "url"
        # To remove all links, run:
        # tutor config save --set INDIGO_FOOTER_NAV_LINKS=[]
        "FOOTER_NAV_LINKS": [
            {"title": "About Us", "url": "/about"},
            {"title": "Blog", "url": "/blog"},
            {"title": "Donate", "url": "/donate"},
            {"title": "Terms of Service", "url": "/tos"},
            {"title": "Privacy Policy", "url": "/privacy"},
            {"title": "Help", "url": "/help"},
            {"title": "Contact Us", "url": "/contact"},
        ],
    },
    "unique": {},
    "overrides": {},
}

# Theme templates
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    str(importlib_resources.files("tutorindigo") / "templates")
)
# This is where the theme is rendered in the openedx build directory
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("indigo", "build/openedx/themes"),
        ("indigo/env.config.jsx", "plugins/mfe/build/mfe"),
    ],
)

# Force the rendering of scss files, even though they are included in a
# "partials" directory
hooks.Filters.ENV_PATTERNS_INCLUDE.add_items(
    [
        r"indigo/lms/static/sass/partials/lms/theme/",
        r"indigo/cms/static/sass/partials/cms/theme/",
    ]
)


# init script: set theme automatically
with open(
    os.path.join(
        str(importlib_resources.files("tutorindigo") / "templates"),
        "indigo",
        "tasks",
        "init.sh",
    ),
    encoding="utf-8",
) as task_file:
    hooks.Filters.CLI_DO_INIT_TASKS.add_item(("lms", task_file.read()))


# Override openedx & mfe docker image names
@hooks.Filters.CONFIG_DEFAULTS.add(priority=hooks.priorities.LOW)
def _override_openedx_docker_image(
    items: list[tuple[str, t.Any]],
) -> list[tuple[str, t.Any]]:
    openedx_image = ""
    mfe_image = ""
    for k, v in items:
        if k == "DOCKER_IMAGE_OPENEDX":
            openedx_image = v
        elif k == "MFE_DOCKER_IMAGE":
            mfe_image = v
    if openedx_image:
        items.append(("DOCKER_IMAGE_OPENEDX", f"{openedx_image}-indigo"))
    if mfe_image:
        items.append(("MFE_DOCKER_IMAGE", f"{mfe_image}-indigo"))
    return items


# Load all configuration entries
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"INDIGO_{key}", value) for key, value in config["defaults"].items()]
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"INDIGO_{key}", value) for key, value in config["unique"].items()]
)
hooks.Filters.CONFIG_OVERRIDES.add_items(list(config["overrides"].items()))


# MFEs that get the Indigo brand package at image build time.
# Header/footer stay each MFE's native chrome (no PLUGIN_SLOTS overrides).
#
# Every MFE already inherits the TitanEd design tokens (colors, typography,
# spacing, buttons, forms, links, dropdowns, shared header/footer chrome) at
# runtime via MFE_CONFIG["PARAGON_THEME_URLS"] below, which is NOT scoped to
# this list -- it applies to every MFE unconditionally. What this list
# actually controls is narrower: which MFEs get the '@edx/brand' fork
# installed at Docker build time, which is what supplies the TitanEd
# logo/favicon/self-hosted font assets baked into that MFE's bundle. Without
# being in this list, an MFE still renders with TitanEd colors/spacing/buttons,
# but shows the stock Open edX logo in its header.
#
# Public / learner-facing MFEs:
indigo_styled_mfes = [
    "learning",
    "learner-dashboard",
    "profile",
    "account",
    "discussions",
    "authoring",
    "catalog",
    # Staff-only / internal MFEs (not learner-facing, but must still match the
    # brand -- these reuse the exact same shared header/footer components as
    # the public MFEs above, e.g. Communications + ORA Grading render
    # `LearningHeader`/`Header` with `.learning-header`, and Admin Console
    # renders `StudioHeader` -- all already styled generically in
    # tels-brand-openedx/paragon/_header.scss + _footer.scss):
    "gradebook",
    "ora-grading",
    "communications",
    "admin-console",
]

for mfe in indigo_styled_mfes:
    hooks.Filters.ENV_PATCHES.add_items(
        [
            (
                f"mfe-dockerfile-post-npm-install-{mfe}",
                """
RUN npm install '@edx/brand@github:@TitanEd/tels-brand-openedx#native-tels-brand-openedx'
""",  # noqa: E501
            ),
        ]
    )

hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-dockerfile-post-npm-install-authn",
        "RUN npm install '@edx/brand@github:@TitanEd/tels-brand-openedx#native-tels-brand-openedx'",
    )
)

# Settings / asset patches only — no Indigo footer/logo/header widgets.
for path in glob(
    os.path.join(str(importlib_resources.files("tutorindigo") / "patches"), "*")
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))

# TitanEd brand CSS — flip BRAND_THEME_SOURCE between "development", "deployed"
# and "live". Switch here ↓
BRAND_THEME_SOURCE = "live"  # "development" | "deployed" | "live"

# `default` = full Paragon CSS; `brandOverride` = TitanEd tokens (+ catalog styles).
PARAGON_VERSION = "23.14.9"
PARAGON_CDN = f"https://cdn.jsdelivr.net/npm/@openedx/paragon@{PARAGON_VERSION}/dist"

BRAND_THEME_DEVELOPMENT = "http://localhost:3000"
BRAND_THEME_DEPLOYED = (
    "https://raw.githubusercontent.com/TitanEd/tels-brand-openedx/"
    "refs/heads/native-tels-brand-openedx/dist"
)
# "live": brandOverride is served by the ui_configuration Django app
# (control-panel repo) instead of straight from GitHub. That endpoint
# fetches BRAND_THEME_DEPLOYED itself server-side and layers a live,
# admin-editable `:root {...}` color override on top of it (see
# control-panel/ui_configuration/README.md and tels_ulmo/CLAUDE.md §9) --
# so a color change made in Django admin reaches every MFE on its next
# page load with no `make build`, no `git push`, and no Tutor rebuild.
# Typography/spacing/layout/component tokens are untouched by this path
# and still come from BRAND_THEME_DEPLOYED via that same server-side fetch.
#
# HOW THE URL BELOW GETS BUILT -- read this before touching it, this took
# two wrong attempts to get right:
#
# Attempt 1 was `{{ LMS_ROOT_URL }}` (Jinja syntax): FAILED outright --
# `tutor config save` raised "Missing configuration value: 'LMS_ROOT_URL' is
# undefined". `LMS_ROOT_URL` isn't a Tutor/Jinja config variable at all --
# it's a plain Python variable Tutor's own lms settings template defines
# *later in the same rendered file* (`LMS_ROOT_URL = "http://{}".format(
# LMS_BASE)`), so it doesn't exist yet when Jinja renders this patch.
#
# Attempt 2 was `{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://
# {{ LMS_HOST }}` (genuine Jinja config variables this time, and it DID
# render without error) -- but it's *silently wrong* in `tutor dev` mode:
# it always omits the port, which is only correct behind Caddy on 80/443
# (`tutor local`/production). In `tutor dev`, LMS is exposed directly on
# `:8000` with no reverse proxy in front, so this produced
# "http://local.openedx.io/..." (port 80, nothing listening) instead of
# "http://local.openedx.io:8000/...". `tutor config save` succeeded, the
# rendered JSON looked fine, curling it directly even returned 200 (it was
# just resolving to whatever happens to be on port 80) -- the only way this
# surfaced was an actual browser fetch failing silently, no CSS applied,
# no visible error. Lesson: do not hand-roll host:port construction here.
#
# The FIX: reference the real `LMS_ROOT_URL` Python variable after all --
# just not via Jinja. Since it's a plain Python name already correctly
# computed per run-mode (WITH the dev port, WITHOUT one behind Caddy) by
# the time our patch's line executes, we build the dict with a placeholder
# string here in plugin.py, then splice a real `+ LMS_ROOT_URL +` Python
# expression into the *rendered* JSON text below (see `_splice_lms_root_url`)
# so the generated settings.py line becomes valid Python that references
# the bare `LMS_ROOT_URL` name at Django-settings-execution time, not at
# Jinja-render time or at this plugin.py's own load time.
_LMS_ROOT_URL_PLACEHOLDER = "__LMS_ROOT_URL_PLACEHOLDER__"
BRAND_THEME_LIVE = f"{_LMS_ROOT_URL_PLACEHOLDER}/ui_configuration/theme"

BRAND_THEME_BASES = {
    "development": BRAND_THEME_DEVELOPMENT,
    "deployed": BRAND_THEME_DEPLOYED,
    "live": BRAND_THEME_LIVE,
}
BRAND_DIST = BRAND_THEME_BASES[BRAND_THEME_SOURCE].rstrip("/")

paragon_theme_urls = {
    "core": {
        "urls": {
            "default": f"{PARAGON_CDN}/core.min.css",
            "brandOverride": f"{BRAND_DIST}/core.min.css",
        },
    },
    "defaults": {
        "light": "light",
        "dark": "dark",
    },
    "variants": {
        "light": {
            "urls": {
                "default": f"{PARAGON_CDN}/light.min.css",
                "brandOverride": f"{BRAND_DIST}/light.min.css",
            },
        },
        "dark": {
            "urls": {
                "default": f"{PARAGON_CDN}/dark.min.css",
                "brandOverride": f"{BRAND_DIST}/dark.min.css",
            },
        },
    },
}

paragon_theme_urls_json = json.dumps(paragon_theme_urls)

if BRAND_THEME_SOURCE == "live":
    # Break out of the JSON string literal at the placeholder and splice in
    # a real Python string-concatenation expression instead, so the
    # generated settings.py line ends up referencing the bare `LMS_ROOT_URL`
    # name (see the long comment above `_LMS_ROOT_URL_PLACEHOLDER`) rather
    # than a JSON-quoted copy of the placeholder text itself.
    #   '"__LMS_ROOT_URL_PLACEHOLDER__/foo"'   (JSON string, wrong)
    #     becomes
    #   '"" + LMS_ROOT_URL + "/foo"'           (Python expression, correct)
    placeholder_count = paragon_theme_urls_json.count(f'"{_LMS_ROOT_URL_PLACEHOLDER}')
    assert placeholder_count == 3, (  # core + light + dark brandOverride URLs
        f"tutorindigo/plugin.py: expected exactly 3 occurrences of the "
        f"LMS_ROOT_URL placeholder in PARAGON_THEME_URLS (one each for "
        f"core/light/dark brandOverride), found {placeholder_count}. "
        f"paragon_theme_urls's shape changed without updating this splice -- "
        f"fix this before running `tutor config save`, a silent mismatch "
        f"here previously shipped a broken (wrong-port) brandOverride URL "
        f"with no visible error anywhere except an actual browser fetch."
    )
    paragon_theme_urls_json = paragon_theme_urls_json.replace(
        f'"{_LMS_ROOT_URL_PLACEHOLDER}',
        '"" + LMS_ROOT_URL + "',
    )

# Logo / footer-logo / favicon -- served by the same ui_configuration app,
# same "live" feature flag. Unlike PARAGON_THEME_URLS above, these are
# simple single-value assignments (not nested inside a json.dumps() JSON
# blob), so LMS_ROOT_URL can be referenced directly as Python source here --
# no placeholder/splice trick needed for this part.
#
# All three of LOGO_URL/LOGO_WHITE_URL/LOGO_TRADEMARK_URL point at the same
# /ui_configuration/logo endpoint: the stock (pre-"live") config already
# pointed all three at the identical theming-asset URL, so nothing is lost
# by unifying them behind one admin-uploaded image. FOOTER_LOGO_URL is
# best-effort -- see control-panel/ui_configuration/views.py's
# footer_logo_redirect docstring for why.
logo_favicon_settings = ""
if BRAND_THEME_SOURCE == "live":
    logo_favicon_settings = """
MFE_CONFIG["LOGO_URL"] = LMS_ROOT_URL + "/ui_configuration/logo"
MFE_CONFIG["LOGO_WHITE_URL"] = LMS_ROOT_URL + "/ui_configuration/logo"
MFE_CONFIG["LOGO_TRADEMARK_URL"] = LMS_ROOT_URL + "/ui_configuration/logo"
MFE_CONFIG["FOOTER_LOGO_URL"] = LMS_ROOT_URL + "/ui_configuration/footer-logo"
MFE_CONFIG["FAVICON_URL"] = LMS_ROOT_URL + "/ui_configuration/favicon"
"""

fstring = f"""
MFE_CONFIG["PARAGON_THEME_URLS"] = {paragon_theme_urls_json}
{logo_favicon_settings}
"""

hooks.Filters.ENV_PATCHES.add_item(("mfe-lms-common-settings", fstring))
