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
        # CONTROL_PANEL_INSTALL_FROM_GIT: set to true ONLY on environments
        # that don't already have control-panel mounted from local disk --
        # i.e. UAT/prod, never local dev:
        #   tutor config save --set INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT=true
        "CONTROL_PANEL_INSTALL_FROM_GIT": False,
        # CONTROL_PANEL_REPO_REF: which branch/tag/commit of control-panel
        # to install. Override per environment, e.g.
        #   tutor config save --set INDIGO_CONTROL_PANEL_REPO_REF=uat
        # Defaults to "main" -- change this if that isn't control-panel's
        # actual default/stable branch.
        "CONTROL_PANEL_REPO_REF": "main",
        # CONTROL_PANEL_REPO_TOKEN: a GitHub Personal Access Token with
        # read-only access to TitanEd/control-panel (it's a private repo).
        # MUST be set per-environment -- there is no safe default:
        #   tutor config save --set INDIGO_CONTROL_PANEL_REPO_TOKEN=<token>
        # Use a fine-grained PAT scoped to *only* this one repo, read-only,
        # not a classic all-repos token -- if it ever leaks, the blast
        # radius is one private repo, not the whole GitHub org. This value
        # lives in config.yml in plaintext, same as every other secret this
        # deployment already stores there (DB passwords, JWT keys, etc.) --
        # protect config.yml itself (file permissions, EC2 instance access
        # control, never commit it to git) rather than trying to avoid this
        # storage mechanism. See tutorindigo's install-control-panel patch
        # below for the "Docker BuildKit secret mount" alternative if a
        # stricter, zero-token-at-rest posture is ever needed instead.
        "CONTROL_PANEL_REPO_TOKEN": "",
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

indigo_styled_mfes = [
    "learning",
    "learner-dashboard",
    "profile",
    "account",
    "discussions",
    "authoring",
    "catalog",
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

hooks.Filters.ENV_PATCHES.add_item(
    (
        "openedx-dockerfile-post-python-requirements",
        """
{% if INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT %}
{% if INDIGO_CONTROL_PANEL_REPO_TOKEN %}
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared $PIP_COMMAND install 'git+https://{{ INDIGO_CONTROL_PANEL_REPO_TOKEN }}@github.com/TitanEd/control-panel.git@{{ INDIGO_CONTROL_PANEL_REPO_REF }}'
{% else %}
RUN echo "ERROR: INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT is true but INDIGO_CONTROL_PANEL_REPO_TOKEN is not set. control-panel (the private repo the ui_configuration Django app lives in) cannot be installed without it. Fix: tutor config save --set INDIGO_CONTROL_PANEL_REPO_TOKEN=<your-github-token> (use a fine-grained, read-only, single-repo-scoped PAT), then rebuild." && exit 1
{% endif %}
{% endif %}
""",
    )
)
