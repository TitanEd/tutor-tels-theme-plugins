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
        # Marketing URLs for CustomHeader + IndigoFooter — overridable via tutor
        # config. Tutor's default MFE routing serves the "public" app at
        # ${MFE_HOST}/public, not the site root, so these work both from the
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
# Header + footer overrides
#
# Footer: hide native default_contents and insert IndigoFooter on footer.v1
# (studio_footer.v1 for authoring). Same widget on every listed MFE.
#
# Header: insert CustomHeader on the host slot each MFE *actually mounts*.
# Slot ids are not interchangeable — applying header_desktop.v1 to a
# LearningHeader app (or header.v1 to an MFE that never mounts that slot)
# silently no-ops. HEADER_REPLACEMENT_SLOTS is the source of truth.
#
#   public            empty HeaderSlot → header.v1 (insert only; no native default)
#   account/profile/  native <Header /> → header_desktop.v1 + header_mobile.v1
#   gradebook/        (Hide native default, insert CustomHeader on both so
#   learner-dashboard  Paragon desktop/mobile breakpoints each show one bar)
#   learning          HeaderSlot → header_learning.v1, plus desktop/mobile
#                     for pages that still render plain <Header />
#   discussions/      LearningHeader has no host slot in upstream git.
#   communications/   Tutor wraps <Header /> at image build
#   ora-grading       (mfe-dockerfile-pre-npm-build-*) so header_learning.v1 exists.
#
# Authn has no site header. Authoring / admin-console keep StudioHeader.
# ---------------------------------------------------------------------------

# Native <Header /> (DesktopHeaderSlot + MobileHeaderSlot inside
# @edx/frontend-component-header). Hide default on both; CustomHeader has
# its own 900px collapse so each viewport still shows one marketing bar.
_DESKTOP_HEADER_SLOTS: list[tuple[str, bool, str]] = [
    ("org.openedx.frontend.layout.header_desktop.v1", True, "custom_header_desktop"),
    ("org.openedx.frontend.layout.header_mobile.v1", True, "custom_header_mobile"),
]

# LearningHeader host (learning MFE already ships HeaderSlot; discussions /
# communications / ora-grading get the same slot via a Dockerfile wrap).
_LEARNING_HEADER_SLOTS: list[tuple[str, bool, str]] = [
    ("org.openedx.frontend.layout.header_learning.v1", True, "custom_header"),
]

# mfe -> [(slot_id, hide_native_default, widget_id)]
HEADER_REPLACEMENT_SLOTS: dict[str, list[tuple[str, bool, str]]] = {
    "public": [
        ("org.openedx.frontend.layout.header.v1", False, "custom_header"),
    ],
    "account": _DESKTOP_HEADER_SLOTS,
    "profile": _DESKTOP_HEADER_SLOTS,
    "gradebook": _DESKTOP_HEADER_SLOTS,
    "learner-dashboard": _DESKTOP_HEADER_SLOTS,
    "learning": _LEARNING_HEADER_SLOTS + _DESKTOP_HEADER_SLOTS,
    "discussions": _LEARNING_HEADER_SLOTS,
    "communications": _LEARNING_HEADER_SLOTS,
    "ora-grading": _LEARNING_HEADER_SLOTS,
}

HEADER_STYLED_MFES = list(HEADER_REPLACEMENT_SLOTS)

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


def _custom_header_plugins(widget_id: str, hide_default: bool) -> str:
    """Insert CustomHeader. Hide native default_contents only when the slot
    already has a header (empty public HeaderSlot must not Hide — there is
    nothing to hide, and Hide-without-default is how the bar disappeared).
    """
    hide = """
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            },
""" if hide_default else ""
    return f"""{hide}
            {{
                op: PLUGIN_OPERATIONS.Insert,
                widget: {{
                    id: '{widget_id}',
                    type: DIRECT_PLUGIN,
                    priority: 1,
                    RenderWidget: CustomHeader,
                }},
            }},
"""


def _add_footer(mfe: str, slot: str = "org.openedx.frontend.layout.footer.v1") -> None:
    PLUGIN_SLOTS.add_item((mfe, slot, FOOTER_PLUGINS))


def _add_custom_header_slots(mfe: str) -> None:
    for slot_id, hide_default, widget_id in HEADER_REPLACEMENT_SLOTS[mfe]:
        PLUGIN_SLOTS.add_item(
            (mfe, slot_id, _custom_header_plugins(widget_id, hide_default))
        )


for mfe in HEADER_STYLED_MFES:
    _add_footer(mfe)
    _add_custom_header_slots(mfe)

# authoring (Studio) has its own header, unrelated to
# @edx/frontend-component-header — only its footer slot is shared.
_add_footer("authoring", "org.openedx.frontend.layout.studio_footer.v1")


# LearningHeader apps do not mount header_learning.v1 in upstream source.
# Wrap their <Header /> at image build (after COPY of MFE src) so PLUGIN_SLOTS
# can hide the native header and insert CustomHeader — no MFE git changes.
LEARNING_HEADER_WRAP_FILES = {
    "discussions": "src/discussions/discussions-home/DiscussionsHome.jsx",
    "communications": "src/components/page-container/PageContainer.jsx",
    "ora-grading": "src/App.jsx",
}


def _learning_header_wrap_dockerfile(relpath: str) -> str:
    path_js = json.dumps(relpath)
    return f"""
RUN node <<'EOF'
const fs = require('fs');
const p = {path_js};
let t = fs.readFileSync(p, 'utf8');
if (t.includes('org.openedx.frontend.layout.header_learning.v1')) {{
  process.exit(0);
}}
const headerImport = "import {{ LearningHeader as Header }} from '@edx/frontend-component-header';";
if (!t.includes(headerImport)) {{
  console.error('CustomHeader wrap: LearningHeader import not found in', p);
  process.exit(1);
}}
if (!t.includes('@openedx/frontend-plugin-framework')) {{
  t = t.replace(
    headerImport,
    "import {{ PluginSlot }} from '@openedx/frontend-plugin-framework';\\n" + headerImport
  );
}}
const wrapped = t.replace(
  /<Header([\\s\\S]*?)\\/>/,
  '<PluginSlot id="org.openedx.frontend.layout.header_learning.v1"><Header$1/></PluginSlot>'
);
if (wrapped === t) {{
  console.error('CustomHeader wrap: <Header /> not found in', p);
  process.exit(1);
}}
fs.writeFileSync(p, wrapped);
console.log('Wrapped LearningHeader in', p);
EOF
"""


for _mfe, _relpath in LEARNING_HEADER_WRAP_FILES.items():
    hooks.Filters.ENV_PATCHES.add_item(
        (f"mfe-dockerfile-pre-npm-build-{_mfe}", _learning_header_wrap_dockerfile(_relpath))
    )


# TitanEd brand CSS — flip BRAND_THEME_SOURCE between "development" and "deployed".
# Switch here ↓
BRAND_THEME_SOURCE = "deployed"  # "development" | "deployed"

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
