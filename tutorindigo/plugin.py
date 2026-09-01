from __future__ import annotations

import itertools
import json
import os
import typing as t
from glob import glob

import importlib_resources
from tutor import hooks
from tutor.__about__ import __version_suffix__
from tutormfe.hooks import PLUGIN_SLOTS

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
        # Marketing header (native @edx/frontend-component-header, see
        # HEADER_STYLED_MFES below) + footer (IndigoFooter) — URLs
        # overridable via tutor config. Default to the public MFE's own route
        # (Tutor's default MFE routing serves the "public" app at
        # ${MFE_HOST}/public, not the site root) so these work both from the
        # public MFE itself and from every other MFE's footer linking back to
        # it. Override HOME_URL if your deployment mounts the public MFE
        # somewhere else, e.g.:
        #   tutor config save --set 'INDIGO_HOME_URL="https://learn.example.com"'
        # COURSES_URL: public MFE /public/courses (search submits here with ?q=).
        # LEARNER_DASHBOARD_URL is usually set by Tutor MFE; override if needed.
        "HOME_URL": "/public",
        "COURSES_URL": "/public/courses",
        "ABOUT_URL": "/public/about",
        "CONTACT_URL": "/public/contact",
        "PRIVACY_URL": "/public/privacy",
        "TERMS_URL": "/public/terms",
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

for mfe in indigo_styled_mfes:
    hooks.Filters.ENV_PATCHES.add_items(
        [
            (
                f"mfe-dockerfile-post-npm-install-{mfe}",
                "RUN npm install '@edx/brand@github:@TitanEd/tels-brand-openedx#native-plus-template-a-tels-brand-openedx'",  # noqa: E501
            ),
        ]
    )

# Include js file in lms main.html, main_django.html, and certificate.html

hooks.Filters.ENV_PATCHES.add_items(
    [
        # for production
        (
            "openedx-common-assets-settings",
            """
javascript_files = ['base_application', 'application', 'certificates_wv']
dark_theme_filepath = ['indigo/js/dark-theme.js']

for filename in javascript_files:
    if filename in PIPELINE['JAVASCRIPT']:
        PIPELINE['JAVASCRIPT'][filename]['source_filenames'] += dark_theme_filepath
""",
        ),
        # for development
        (
            "openedx-lms-development-settings",
            """
javascript_files = ['base_application', 'application', 'certificates_wv']
dark_theme_filepath = ['indigo/js/dark-theme.js']

for filename in javascript_files:
    if filename in PIPELINE['JAVASCRIPT']:
        PIPELINE['JAVASCRIPT'][filename]['source_filenames'] += dark_theme_filepath

MFE_CONFIG['INDIGO_ENABLE_DARK_TOGGLE'] = {{ INDIGO_ENABLE_DARK_TOGGLE }}
MFE_CONFIG['INDIGO_FOOTER_NAV_LINKS'] = {{ INDIGO_FOOTER_NAV_LINKS }}
""",
        ),
        (
            "openedx-lms-production-settings",
            """
MFE_CONFIG['INDIGO_ENABLE_DARK_TOGGLE'] = {{ INDIGO_ENABLE_DARK_TOGGLE }}
MFE_CONFIG['INDIGO_FOOTER_NAV_LINKS'] = {{ INDIGO_FOOTER_NAV_LINKS }}
""",
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


# ---------------------------------------------------------------------------
# Header + footer overrides — same method as the reference tutor-indigo
# theme plugin (VigyanShaala-Tech/tutor-vigyanshaala-theme-plugin, `release`
# branch): target the PluginSlots that @edx/frontend-component-header and
# @edx/frontend-component-footer render *inside their own components*
# (header_desktop_user_menu_toggle.v1, header_desktop_user_menu.v1,
# header_mobile_user_menu.v1, footer.v1), instead of hiding/replacing the
# app-level "org.openedx.frontend.layout.header.v1" wrapper slot. Those
# inner slots exist as soon as an app renders <Header /> / <LearningHeader />
# / <FooterSlot />, whether or not that app's own source wraps them in an
# outer PluginSlot — so no per-MFE source-file patching is needed. The
# Language dropdown and dark-mode toggle are simply not part of this
# override, so they no longer render in the header at all.
#
# IMPORTANT — the ids differ by which header component an MFE renders, and
# by its exact pinned @edx/frontend-component-header version (verified below
# against each MFE's locked version on this project's release/ulmo.1 pin,
# 2026-08-31 — re-verify if that pin ever moves):
#   - account/profile/gradebook/learner-dashboard render the plain
#     <Header /> (DesktopHeader/MobileHeader) -> "header_desktop_user_menu*"
#     / "header_mobile_user_menu.v1" ids.
#   - discussions/communications/ora-grading/learning render
#     <LearningHeader /> instead -> a *different* set of ids,
#     "header_learning_user_menu*". Blanket-applying the desktop ids to
#     these (an earlier version of this file did) silently no-ops there —
#     the PluginSlot with that id simply never exists, so nothing renders.
#   - The user-menu *toggle* (avatar + name button) is its own separate
#     PluginSlot that didn't exist before @edx/frontend-component-header
#     6.6.0. profile (6.4.2) and ora-grading (6.4.0) predate it, so only the
#     dropdown *contents* can be overridden there — the toggle itself stays
#     native. profile gets a mergeProps fallback (see USERNAME_FALLBACK_MFES
#     below) that at least swaps in the full display name + photo;
#     LearningHeader has no equivalent override point for ora-grading.
HEADER_USER_MENU_SLOTS: dict[str, tuple[str, str, str | None]] = {
    # mfe -> (header component, dropdown-contents slot id, toggle slot id or None)
    # DesktopHeader apps
    "account": (
        "desktop",
        "org.openedx.frontend.layout.header_desktop_user_menu.v1",
        "org.openedx.frontend.layout.header_desktop_user_menu_toggle.v1",
    ),  # @edx/frontend-component-header 6.6.1
    "profile": (
        "desktop",
        "org.openedx.frontend.layout.header_desktop_user_menu.v1",
        None,
    ),  # 6.4.2 — no toggle slot yet
    "gradebook": (
        "desktop",
        "org.openedx.frontend.layout.header_desktop_user_menu.v1",
        "org.openedx.frontend.layout.header_desktop_user_menu_toggle.v1",
    ),  # 6.6.1
    "learner-dashboard": (
        "desktop",
        "org.openedx.frontend.layout.header_desktop_user_menu.v1",
        "org.openedx.frontend.layout.header_desktop_user_menu_toggle.v1",
    ),  # 6.6.1
    # LearningHeader apps
    "discussions": (
        "learning",
        "org.openedx.frontend.layout.header_learning_user_menu.v1",
        "org.openedx.frontend.layout.header_learning_user_menu_toggle.v1",
    ),  # 6.6.1
    "communications": (
        "learning",
        "org.openedx.frontend.layout.header_learning_user_menu.v1",
        "org.openedx.frontend.layout.header_learning_user_menu_toggle.v1",
    ),  # 6.6.1
    "ora-grading": (
        "learning",
        "org.openedx.frontend.layout.header_learning_user_menu.v1",
        None,
    ),  # 6.4.0 — no toggle slot yet
    "learning": (
        "learning",
        "org.openedx.frontend.layout.header_learning_user_menu.v1",
        "org.openedx.frontend.layout.header_learning_user_menu_toggle.v1",
    ),  # 8.0.0
}

# DesktopHeader apps also get a separate mobile-viewport slot (LearningHeader
# has no separate mobile variant — one slot covers both).
MOBILE_USER_MENU_SLOT_ID = "org.openedx.frontend.layout.header_mobile_user_menu.v1"

# public isn't part of this table: it's a separately-maintained custom app
# (own build context/image, doesn't declare @edx/frontend-component-header),
# not something this override reaches — it manages its own header.
HEADER_STYLED_MFES = list(HEADER_USER_MENU_SLOTS) + ["public"]

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
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'read_theme_cookie',
                    type: DIRECT_PLUGIN,
                    priority: 2,
                    RenderWidget: AddDarkTheme,
                },
            },
"""

USER_MENU_TOGGLE_PLUGIN = """
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'custom_desktop_user_menu_toggle_avatar',
                    type: DIRECT_PLUGIN,
                    RenderWidget: DesktopUserMenuToggleAvatar,
                },
            },
"""


def _user_menu_items_plugin(widget_id: str) -> str:
    return f"""
            {{
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            }},
            {{
                op: PLUGIN_OPERATIONS.Insert,
                widget: {{
                    id: '{widget_id}',
                    type: DIRECT_PLUGIN,
                    RenderWidget: CustomHeaderUserMenuItem,
                }},
            }},
"""


def _add_footer(mfe: str, slot: str = "org.openedx.frontend.layout.footer.v1") -> None:
    PLUGIN_SLOTS.add_item((mfe, slot, FOOTER_PLUGINS))


def _add_user_menu_slots(mfe: str) -> None:
    """Avatar/name toggle (where that MFE's header version has the slot) +
    admin-aware dropdown contents, on the ids that MFE's *actual* header
    component and pinned package version expose — see HEADER_USER_MENU_SLOTS.
    """
    header_kind, menu_slot_id, toggle_slot_id = HEADER_USER_MENU_SLOTS[mfe]

    if toggle_slot_id:
        PLUGIN_SLOTS.add_item((mfe, toggle_slot_id, USER_MENU_TOGGLE_PLUGIN))

    PLUGIN_SLOTS.add_item(
        (
            mfe,
            menu_slot_id,
            _user_menu_items_plugin("custom_desktop_user_menu_component"),
        )
    )

    if header_kind == "desktop":
        PLUGIN_SLOTS.add_item(
            (
                mfe,
                MOBILE_USER_MENU_SLOT_ID,
                _user_menu_items_plugin("custom_mobile_user_menu_component"),
            )
        )


for mfe in HEADER_STYLED_MFES:
    _add_footer(mfe)
    if mfe in HEADER_USER_MENU_SLOTS:
        _add_user_menu_slots(mfe)

# authoring (Studio) has its own header, unrelated to
# @edx/frontend-component-header — only its footer slot is shared.
_add_footer("authoring", "org.openedx.frontend.layout.studio_footer.v1")

# profile predates the toggle-slot PluginSlot (see HEADER_USER_MENU_SLOTS
# above), so fall back to overriding the username/avatar *props* on the
# native toggle instead, via the outer header_desktop.v1 / header_mobile.v1
# slot (both support mergeProps).
USERNAME_FALLBACK_MFES = {
    "profile": (
        "org.openedx.frontend.layout.header_desktop.v1",
        "org.openedx.frontend.layout.header_mobile.v1",
    ),
}

for _mfe, _slots in USERNAME_FALLBACK_MFES.items():
    for _slot in _slots:
        PLUGIN_SLOTS.add_item(
            (
                _mfe,
                _slot,
                """
            {
                op: PLUGIN_OPERATIONS.Modify,
                widgetId: 'default_contents',
                fn: modifyHeaderUsername,
            },
        """,
            )
        )


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
