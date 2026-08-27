from __future__ import annotations

import itertools
import json
import os
import typing as t
from glob import glob

import importlib_resources
from tutor import hooks
from tutor.__about__ import __version_suffix__
from tutormfe.hooks import MFE_APPS, MFE_ATTRS_TYPE, PLUGIN_SLOTS

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
        "ENABLE_LANGUAGE_MENU": True,
        # Languages shown in the MFE header dropdown (need 2+ to render).
        "SUPPORTED_LANGUAGES": [
            {"value": "en", "label": "English"},
            {"value": "ar", "label": "العربية"},
            {"value": "es-419", "label": "Español (Latinoamérica)"},
            {"value": "fr", "label": "Français"},
            {"value": "pt-pt", "label": "Português"},
            {"value": "zh-cn", "label": "中文 (简体)"},
        ],
        # Marketing footer columns — shown on every MFE (IndigoFooter).
        # titleKey maps to indigo.footer.link.* intl messages in IndigoFooter.jsx.
        "FOOTER_EXPLORE_LINKS": [
            {"titleKey": "home", "url": "/"},
            {"titleKey": "courses", "url": "/courses"},
            {"titleKey": "about", "url": "/about"},
            {"titleKey": "contact", "url": "/contact"},
        ],
        "FOOTER_COMPANY_LINKS": [
            {"titleKey": "about", "url": "/about"},
            {"titleKey": "contact", "url": "/contact"},
        ],
        "FOOTER_SUPPORT_LINKS": [
            {"titleKey": "privacy", "url": "/privacy"},
            {"titleKey": "terms", "url": "/terms"},
        ],
        "FOOTER_CONTACT": {
            "email": "Legal@TitanEd.com",
            "web_url": "https://titaned.com/",
            "web_label": "titaned.com",
            "address_lines": [
                "TitanEd, Gurugram,",
                "Haryana, India",
            ],
        },
        # Legacy flat nav list (kept for backward-compatible MFE_CONFIG).
        "FOOTER_NAV_LINKS": [
            {"title": "About Us", "url": "/about"},
            {"title": "Contact", "url": "/contact"},
        ],
        # Social icons shown on every MFE footer.
        # name must be one of: facebook, twitter, linkedin, youtube, instagram
        "FOOTER_SOCIAL_LINKS": [
            {
                "name": "linkedin",
                "label": "LinkedIn",
                "url": "https://www.linkedin.com/company/titaned",
            },
            {
                "name": "facebook",
                "label": "Facebook",
                "url": "https://titaned.com/",
            },
            {
                "name": "twitter",
                "label": "X (Twitter)",
                "url": "https://titaned.com/",
            },
            {
                "name": "youtube",
                "label": "YouTube",
                "url": "https://titaned.com/",
            },
            {
                "name": "instagram",
                "label": "Instagram",
                "url": "https://titaned.com/",
            },
        ],
        # Marketing header (TelsHeader) + footer (IndigoFooter) — URLs
        # overridable via tutor config. Default to the public MFE's own route
        # (Tutor's default MFE routing serves the "public" app at
        # ${MFE_HOST}/public, not the site root) so these work both from the
        # public MFE itself and from every other MFE's header/footer linking
        # back to it. Override HOME_URL if your deployment mounts the public
        # MFE somewhere else, e.g.:
        #   tutor config save --set 'INDIGO_HOME_URL="https://learn.example.com"'
        # COURSES_URL: public MFE /public/courses (search submits here with ?q=).
        # LEARNER_DASHBOARD_URL is usually set by Tutor MFE; override if needed.
        "HOME_URL": "/public",
        "COURSES_URL": "/public/courses",
        "ABOUT_URL": "/public/about",
        "CONTACT_URL": "/public/contact",
        "PRIVACY_URL": "/public/privacy",
        "TERMS_URL": "/public/terms",
        "HEADER_GUEST_NAV": [
            {"titleKey": "home", "urlKey": "home"},
            {"titleKey": "courses", "urlKey": "courses"},
            {"titleKey": "about", "urlKey": "about"},
            {"titleKey": "contact", "urlKey": "contact"},
        ],
        "HEADER_AUTH_NAV": [
            {"titleKey": "home", "urlKey": "home"},
            {"titleKey": "dashboard", "urlKey": "dashboard"},
            {"titleKey": "courses", "urlKey": "courses"},
            {"titleKey": "about", "urlKey": "about"},
            {"titleKey": "contact", "urlKey": "contact"},
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


#  MFEs that install the Indigo brand package at image build time
indigo_styled_mfes = [
    "learning",
    "learner-dashboard",
    "profile",
    "account",
    "discussions",
    "authoring",
    "authn",
    "gradebook",
    "communications",
    "ora-grading",
    "admin-console",
    "public",
]

# env.config.jsx (Imports.jsx patch) is baked into EVERY styled MFE's image
# and unconditionally imports these packages for the shared TelsHeader /
# IndigoFooter / HeaderControls / LanguageMenu bundle. Not every upstream MFE
# repo declares them (e.g. authoring, discussions, gradebook, learning have
# none of these in package.json), so `npm run build` fails with
# "Module not found" for those apps and the whole `tutor images build mfe`
# aborts. Install them explicitly for every MFE that gets the shared bundle,
# regardless of what its own package.json already has.
MARKETING_CHROME_NPM_DEPS = [
    "@fortawesome/react-fontawesome@^0.2.6",
    "@fortawesome/free-brands-svg-icons@^6.7.2",
    "@fortawesome/free-solid-svg-icons@^6.7.2",
    "universal-cookie@^7.2.2",
]

for mfe in indigo_styled_mfes:
    hooks.Filters.ENV_PATCHES.add_items(
        [
            (
                f"mfe-dockerfile-post-npm-install-{mfe}",
                """
RUN npm install '@edx/brand@github:@edly-io/brand-openedx#indigo-2.6.0'
RUN npm install {deps}
""".format(deps=" ".join(f"'{dep}'" for dep in MARKETING_CHROME_NPM_DEPS)),  # noqa: E501
            ),
        ]
    )

# Add react components and patches from tutor-indigo
for path in itertools.chain(
    glob(
        os.path.join(str(importlib_resources.files("tutorindigo") / "components"), "*")
    ),
    glob(os.path.join(str(importlib_resources.files("tutorindigo") / "patches"), "*")),
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))


HEADER_CONTROLS_PLUGIN = """
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'indigo_header_controls',
                    type: DIRECT_PLUGIN,
                    priority: 1,
                    RenderWidget: HeaderControls,
                },
            },
"""

FOOTER_PLUGINS = """
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'indigo_footer',
                    type: DIRECT_PLUGIN,
                    priority: 1,
                    RenderWidget: IndigoFooter,
                },
            },
"""

# Full Lovable-style marketing header (public MFE HeaderSlot).
TELS_HEADER_PLUGINS = """
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'tels_header',
                    type: DIRECT_PLUGIN,
                    priority: 1,
                    RenderWidget: TelsHeader,
                },
            },
"""


def _add_footer(mfe: str, slot: str = "org.openedx.frontend.layout.footer.v1") -> None:
    PLUGIN_SLOTS.add_item((mfe, slot, FOOTER_PLUGINS))


def _add_tels_header(mfe: str, slot: str = "org.openedx.frontend.layout.header.v1") -> None:
    PLUGIN_SLOTS.add_item((mfe, slot, TELS_HEADER_PLUGINS))


def _add_header_controls_slots(mfe: str) -> None:
    """
    Language + dark-mode in header for logged-in AND logged-out users.

    Desktop secondary menu is only rendered when logged in, so also inject into
    the logged-out items slot. Same idea for mobile.
    """
    for slot in (
        "desktop_secondary_menu_slot",
        "desktop_logged_out_items_slot",
        "mobile_logged_out_items_slot",
        "org.openedx.frontend.layout.header_mobile_user_menu_trigger.v1",
    ):
        PLUGIN_SLOTS.add_item((mfe, slot, HEADER_CONTROLS_PLUGIN))


# LOW priority so public (added by other Tutor plugins) is present.
@MFE_APPS.add(priority=hooks.priorities.LOW)  # type: ignore
def _add_header_language_and_dark_mode(
    mfes: dict[str, MFE_ATTRS_TYPE],
) -> dict[str, MFE_ATTRS_TYPE]:
    """Attach language dropdown + dark-mode switch to every registered MFE."""
    for mfe in mfes:
        name = str(mfe)

        # Public: TelsHeader via HeaderSlot (Template A public pages).
        if name == "public":
            _add_tels_header(name)
            _add_footer(name)
            continue

        # LearningHeader MFEs (learning + discussions) use learning_* slots,
        # not desktop_secondary_menu_slot from the standard site header.
        if name in ("learning", "discussions"):
            PLUGIN_SLOTS.add_items(
                [
                    (
                        name,
                        "learning_help_slot",
                        """
        {
            op: PLUGIN_OPERATIONS.Hide,
            widgetId: 'default_contents',
        },
"""
                        + HEADER_CONTROLS_PLUGIN,
                    ),
                    (
                        name,
                        "learning_logged_out_items_slot",
                        HEADER_CONTROLS_PLUGIN,
                    ),
                ]
            )
            _add_footer(name)
            continue

        if name == "authoring":
            PLUGIN_SLOTS.add_items(
                [
                    (
                        "authoring",
                        "org.openedx.frontend.layout.studio_header_search_button_slot.v1",
                        HEADER_CONTROLS_PLUGIN,
                    ),
                ]
            )
            _add_footer("authoring", "org.openedx.frontend.layout.studio_footer.v1")
            continue

        # Standard Header (account, profile, learner-dashboard, …)
        _add_header_controls_slots(name)
        _add_footer(name)

    return mfes


# TitanEd brand CSS — flip BRAND_THEME_SOURCE between "development" and "deployed".
# Switch here ↓
BRAND_THEME_SOURCE = "development"  # "development" | "deployed"

# `default` = full Paragon CSS; `brandOverride` = TitanEd tokens (Template A / public).
PARAGON_VERSION = "23.14.9"
PARAGON_CDN = f"https://cdn.jsdelivr.net/npm/@openedx/paragon@{PARAGON_VERSION}/dist"

BRAND_THEME_DEVELOPMENT = "http://localhost:3000"
BRAND_THEME_DEPLOYED = (
    "https://raw.githubusercontent.com/TitanEd/tels-brand-openedx/"
    "refs/heads/native-plus-template-a-tels-brand-openedx/dist"
)

BRAND_THEME_BASES = {
    "development": BRAND_THEME_DEVELOPMENT,
    "deployed": BRAND_THEME_DEPLOYED,
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

fstring = f"""
MFE_CONFIG["PARAGON_THEME_URLS"] = {json.dumps(paragon_theme_urls)}
"""

hooks.Filters.ENV_PATCHES.add_item(("mfe-lms-common-settings", fstring))

# NOTE: Do NOT replace logo_slot with ThemedLogo — it breaks header logos that
# already use MFE_CONFIG LOGO_URL / design-token header styles (tels_brand_image).
