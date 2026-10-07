from __future__ import annotations

import itertools
import json
import os
import typing as t
from glob import glob

import importlib_resources
from tutor import hooks
from tutor.__about__ import __version_suffix__
from tutormfe.hooks import FRONTEND_COMPAT_SLOTS, MFE_APPS, MFE_ATTRS_TYPE, PLUGIN_SLOTS

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
        # Footer links are dictionaries with a "title" and "url"
        # To remove all links, run:
        # tutor config save --set INDIGO_FOOTER_NAV_LINKS=[]
        # Shown in the middle column of the footer (IndigoFooter.jsx); the address,
        # contact email, social links and copyright come from the theme
        # configuration page (/theme/ui_configuration/#footer-settings).
        "FOOTER_NAV_LINKS": [
            {"title": "About Us", "url": "/about"},
            {"title": "Terms of Service", "url": "/tos"},
            {"title": "Privacy Policy", "url": "/privacy"},
            {"title": "Contact Us", "url": "/contact"},
        ],
        # ---- TitanEd repositories and branches -------------------------
        # Installing this plugin wires the TELS repos together; change a branch
        # here (or with `tutor config save --set ...`) and everything that
        # depends on it follows:
        #   control-panel      INDIGO_CONTROL_PANEL_REPO_REF -> pip install into
        #                      the openedx image (unless mounted from disk)
        #   tels-brand-openedx INDIGO_BRAND_REPO_REF -> @edx/brand in the MFE
        #                      image, the "deployed" theme URL, and the brand CSS
        #                      control-panel's live theme is built on
        "BRAND_REPO": "TitanEd/tels-brand-openedx",
        "BRAND_REPO_REF": "tels-template-1-brand",
        # TitanEd brand CSS source for the MFEs (PARAGON_THEME_URLS):
        #   "live"        -> control-panel's ui_configuration app
        #                    (LMS_ROOT_URL/ui_configuration/theme/*): the brand
        #                    CSS with the design tokens saved on the theme
        #                    configuration page (/theme/ui_configuration/).
        #                    A save there applies on the next page load, no
        #                    restart or rebuild needed.
        #   "deployed"    -> tels-brand-openedx dist/ on GitHub
        #                    (INDIGO_BRAND_THEME_DEPLOYED_URL)
        #   "development" -> local tels-brand-openedx `npm run serve`
        #                    (INDIGO_BRAND_THEME_DEVELOPMENT_URL)
        #   Any other value behaves like "deployed".
        #   tutor config save --set INDIGO_BRAND_THEME_SOURCE=live
        "BRAND_THEME_SOURCE": "live",
        "BRAND_THEME_DEVELOPMENT_URL": "http://localhost:3000",
        "BRAND_THEME_DEPLOYED_URL": (
            "https://raw.githubusercontent.com/{{ INDIGO_BRAND_REPO }}/refs/heads/{{ INDIGO_BRAND_REPO_REF }}/dist"
        ),
        # Full Paragon CSS used as the `default` URL next to `brandOverride`
        # for legacy (frontend-platform) MFEs.
        "PARAGON_VERSION": "23.14.9",
        # npm package installed as @edx/brand in the MFE image (build time):
        # logos, favicon and SCSS of tels-brand-openedx at INDIGO_BRAND_REPO_REF.
        "BRAND_PACKAGE": "@edx/brand@github:{{ INDIGO_BRAND_REPO }}#{{ INDIGO_BRAND_REPO_REF }}",
        # CONTROL_PANEL_INSTALL_FROM_GIT: install control-panel from GitHub
        # into the openedx image. Skipped automatically when control-panel is
        # mounted from local disk (`tutor mounts add .../control-panel`, local
        # dev); set to false to never install it.
        "CONTROL_PANEL_INSTALL_FROM_GIT": True,
        # CONTROL_PANEL_REPO_REF: which branch/tag/commit of control-panel
        # to install, e.g.
        #   tutor config save --set INDIGO_CONTROL_PANEL_REPO_REF=uat
        "CONTROL_PANEL_REPO_REF": "tels-template-1",
        # CONTROL_PANEL_REPO_TOKEN: a fine-grained, read-only GitHub PAT scoped
        # to TitanEd/control-panel only (private repo). MUST be set per
        # environment that installs from GitHub; it ends up in config.yml and
        # in the image build history:
        #   tutor config save --set INDIGO_CONTROL_PANEL_REPO_TOKEN=<token>
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


#  MFEs that are styled using Indigo
indigo_styled_mfes = [
    "learning",
    "learner-dashboard",
    "profile",
    "account",
    "discussions",
    "authoring",
    "catalog",
    # template-1: staff MFEs and the public marketing MFE get the same brand
    # package, header and footer as the learner MFEs.
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
                """
RUN npm install '{{ INDIGO_BRAND_PACKAGE }}'
""",  # noqa: E501
            ),
        ]
    )

hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-dockerfile-post-npm-install-authn",
        "RUN npm install '{{ INDIGO_BRAND_PACKAGE }}'",
    )
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
# TitanEd MFEs that are not stock openedx/frontend-app-* builds. Registered
# with tutor-mfe here (same MFE_APPS filter a standalone "add my MFE" plugin
# would use) so the app id, its brand/header/footer patches and its dev port
# live in one place. The app id "public" must match indigo_styled_mfes and
# HEADER_REPLACEMENT_SLOTS below; the live URL is {MFE_HOST}/public/. A
# standalone plugin registering the same id with the same values is harmless.
# ---------------------------------------------------------------------------
FORKED_MFE_APPS: dict[str, dict[str, str | int]] = {
    "public": {
        "repository": "https://github.com/TitanEd/frontend-app-tels-public.git",
        "port": 2024,
        "version": "native-plus-template-a",
    },
}


@MFE_APPS.add()
def _add_forked_mfe_apps(mfes: dict[str, MFE_ATTRS_TYPE]) -> dict[str, MFE_ATTRS_TYPE]:
    mfes.update(FORKED_MFE_APPS)  # type: ignore[arg-type]
    return mfes


# ---------------------------------------------------------------------------
# Template-1 header: CustomHeader on every styled MFE
# (the site footer is INDIGO_FOOTER_SLOT / _add_themed_logo above).
#
# Header: insert CustomHeader on the host slot each MFE *actually mounts*.
# Slot ids are not interchangeable — applying header_desktop.v1 to a
# LearningHeader app (or header.v1 to an MFE that never mounts that slot)
# silently no-ops. HEADER_REPLACEMENT_SLOTS is the source of truth.
#
#   public            empty HeaderSlot → header.v1 (insert only; no native default)
#   account/profile/  native <Header /> → header_desktop.v1 + header_mobile.v1
#   gradebook/        (Hide native default, insert CustomHeader on both so
#   learner-dashboard/ Paragon desktop/mobile breakpoints each show one bar)
#   catalog
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
    "catalog": _DESKTOP_HEADER_SLOTS,  # CatalogHeader wraps the plain <Header />
    "learning": _LEARNING_HEADER_SLOTS + _DESKTOP_HEADER_SLOTS,
    "discussions": _LEARNING_HEADER_SLOTS,
    "communications": _LEARNING_HEADER_SLOTS,
    "ora-grading": _LEARNING_HEADER_SLOTS,
}

HEADER_STYLED_MFES = list(HEADER_REPLACEMENT_SLOTS)

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


def _add_custom_header_slots(mfe: str) -> None:
    for slot_id, hide_default, widget_id in HEADER_REPLACEMENT_SLOTS[mfe]:
        PLUGIN_SLOTS.add_item(
            (mfe, slot_id, _custom_header_plugins(widget_id, hide_default))
        )


for mfe in HEADER_STYLED_MFES:
    _add_custom_header_slots(mfe)



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



# ---------------------------------------------------------------------------
# Header/footer *translation* safety net.
#
# CustomHeader/IndigoFooter's own strings (tels.header.*/indigo.footer.*, and
# the account.user.menu.*/avatarAlt ids from the header's user-menu sub-
# components -- see tutorindigo/components/{CustomHeader,IndigoFooter,
# LanguageMenu,CustomHeaderUserMenu*}.jsx) were added to openedx-translations'
# EXISTING frontend-component-header/frontend-component-footer resources
# (see that repo's transifex.yml) rather than a new one -- deliberately, so
# any MFE that already pulls those two directories via its own
# `pull_translations` Makefile target picks the new ids up with zero
# Makefile changes.
#
# The catch: not every MFE's own Makefile actually lists both directories.
# Confirmed against a built image: frontend-app-learner-dashboard (pulled
# straight from stock openedx/frontend-app-learner-dashboard -- no TitanEd
# fork of it exists to patch, see the repo_map in the workspace root
# CLAUDE.md) pulls frontend-component-footer but NOT frontend-component-
# header at all -- not even the pre-existing upstream header keys, so
# CustomHeader was never translated there, predating this change entirely.
# Since there's no fork to fix and an upstream Makefile can drop a pull
# target at any time independent of this plugin, instead of special-casing
# learner-dashboard (or chasing the next MFE with the same gap), every MFE
# this plugin styles gets one extra Dockerfile step, right after
# `pull_translations` (`mfe-dockerfile-pre-npm-build-<mfe>`, the same slot
# LEARNING_HEADER_WRAP_FILES above uses) that atlas-pulls
# frontend-component-header/-footer itself and merges their per-locale JSON
# into `src/i18n/messages/frontend-platform` -- the one package *every* MFE
# unconditionally pulls and imports (confirmed in frontend-app-authn's and
# frontend-app-learning's own Makefiles) -- so the merged keys reach
# `src/i18n/index.js` regardless of what that particular MFE's own
# pull_translations target does or doesn't list. Re-running this for an MFE
# that already pulls both directories correctly is harmless (same values
# merged twice); `atlas` is already on PATH by this point since the stock
# `pull_translations` step just used it moments earlier in the same image.
# ---------------------------------------------------------------------------
# NOTE: no "public" -> "tels-public" remap here (there used to be one) --
# HEADER_STYLED_MFES already says "public", the correct/actual app id (see
# the FORKED_MFE_APPS comment above); remapping it here was only ever a
# workaround for FORKED_MFE_APPS having the wrong key, now fixed at the
# source instead.
TRANSLATION_SAFETY_NET_MFES = sorted(set(HEADER_STYLED_MFES) | {"authoring"})

_TRANSLATION_SAFETY_NET_DOCKERFILE = """
RUN atlas pull --repository={{ ATLAS_REPOSITORY }} --revision={{ ATLAS_REVISION }} {{ ATLAS_OPTIONS }} \\
    translations/frontend-component-header/src/i18n/messages:/tmp/tels-i18n-safety-net/frontend-component-header \\
    translations/frontend-component-footer/src/i18n/messages:/tmp/tels-i18n-safety-net/frontend-component-footer

RUN node <<'EOF'
const fs = require('fs');
const path = require('path');
const SRC_DIRS = [
  '/tmp/tels-i18n-safety-net/frontend-component-header',
  '/tmp/tels-i18n-safety-net/frontend-component-footer',
];
const DEST_DIR = 'src/i18n/messages/frontend-platform';
fs.mkdirSync(DEST_DIR, { recursive: true });
for (const srcDir of SRC_DIRS) {
  if (!fs.existsSync(srcDir)) continue;
  for (const file of fs.readdirSync(srcDir)) {
    if (!file.endsWith('.json')) continue;
    const srcPath = path.join(srcDir, file);
    const destPath = path.join(DEST_DIR, file);
    const incoming = JSON.parse(fs.readFileSync(srcPath, 'utf8'));
    let existing = {};
    if (fs.existsSync(destPath)) {
      existing = JSON.parse(fs.readFileSync(destPath, 'utf8'));
    }
    const merged = Object.assign({}, existing, incoming);
    fs.writeFileSync(destPath, JSON.stringify(merged));
    console.log('[tels-i18n-safety-net] merged', Object.keys(incoming).length, 'keys from', srcPath, 'into', destPath);
  }
}
EOF
"""

for _mfe in TRANSLATION_SAFETY_NET_MFES:
    hooks.Filters.ENV_PATCHES.add_item(
        (f"mfe-dockerfile-pre-npm-build-{_mfe}", _TRANSLATION_SAFETY_NET_DOCKERFILE)
    )



INDIGO_FOOTER_SLOT = (
    "org.openedx.frontend.layout.footer.v1",
    """
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
""",
)

INDIGO_FOOTER_COMPAT_SLOT = (
    "org.openedx.frontend.layout.footer.v1",
    """
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
""",
)

INDIGO_DESKTOP_SECONDARY_MENU_SLOT = (
    "desktop_secondary_menu_slot",
    """
    {
        op: PLUGIN_OPERATIONS.Insert,
        widget: {
            id: 'theme_switch_button',
            type: DIRECT_PLUGIN,
            RenderWidget: ToggleThemeButton,
        },
    },
""",
)

# Hide the default mobile header (it only shows the logo) and replace it.
INDIGO_MOBILE_HEADER_SLOT = (
    "mobile_header_slot",
    """
    {
        op: PLUGIN_OPERATIONS.Hide,
        widgetId: 'default_contents',
    },
    {
        op: PLUGIN_OPERATIONS.Insert,
        widget: {
            id: 'theme_switch_button',
            type: DIRECT_PLUGIN,
            RenderWidget: MobileViewHeader,
        },
    },
""",
)

INDIGO_LOGO_SLOT = (
    "logo_slot",
    """
    {
        op: PLUGIN_OPERATIONS.Hide,
        widgetId: 'default_contents',
    },
    {
        op: PLUGIN_OPERATIONS.Insert,
        widget: {
            id: 'custom_logo',
            type: DIRECT_PLUGIN,
            RenderWidget: ThemedLogo,
        }
    }
""",
)

# Frontend-base site compatibility
FRONTEND_COMPAT_SLOTS.add_item(("all", *INDIGO_FOOTER_COMPAT_SLOT))
FRONTEND_COMPAT_SLOTS.add_item(("all", *INDIGO_DESKTOP_SECONDARY_MENU_SLOT))
FRONTEND_COMPAT_SLOTS.add_item(("all", *INDIGO_MOBILE_HEADER_SLOT))
FRONTEND_COMPAT_SLOTS.add_item(("all", *INDIGO_LOGO_SLOT))

# The site footer (IndigoFooter) goes on every MFE but authoring, which has the
# Studio footer: see _add_themed_logo below for the MFEs not styled by Indigo.
for mfe in indigo_styled_mfes:
    if mfe != "authoring":
        PLUGIN_SLOTS.add_item((mfe, *INDIGO_FOOTER_SLOT))
    if mfe != "learning":
        PLUGIN_SLOTS.add_item((mfe, *INDIGO_DESKTOP_SECONDARY_MENU_SLOT))
        PLUGIN_SLOTS.add_item((mfe, *INDIGO_MOBILE_HEADER_SLOT))

PLUGIN_SLOTS.add_items(
    [
        (
            # Hide the default Help Link added in plugin slot
            "learning",
            "learning_help_slot",
            """
        {
            op: PLUGIN_OPERATIONS.Hide,
            widgetId: 'default_contents',
        }
        """,
        ),
        (
            "learning",
            "learning_help_slot",
            """
        {
            op: PLUGIN_OPERATIONS.Insert,
            widget: {
                id: 'theme_switch_button',
                type: DIRECT_PLUGIN,
                RenderWidget: ToggleThemeButton,
            },
        },
        """,
        ),
    ]
)

PLUGIN_SLOTS.add_items(
    [
        (
            "authoring",
            "org.openedx.frontend.layout.studio_header_search_button_slot.v1",
            """
        {
            op: PLUGIN_OPERATIONS.Insert,
            widget: {
                priority: 10,
                id: 'custom_notification_tray_before',
                type: DIRECT_PLUGIN,
                RenderWidget: ToggleThemeButton,
            },
        },
        """,
        ),
        (
            "authoring",
            "org.openedx.frontend.layout.studio_footer.v1",
            """
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'read_theme_cookie',
                    type: DIRECT_PLUGIN,
                    priority: 2,
                    RenderWidget: AddDarkTheme,
                },
            },
        """,
        ),
    ]
)

# TitanEd brand CSS, logos and favicon (PARAGON_THEME_URLS for the legacy
# MFEs, FRONTEND_SITE_CONFIG["theme"] for frontend-base sites), from the
# source selected by INDIGO_BRAND_THEME_SOURCE.
# In "live" mode every URL points at control-panel's ui_configuration app,
# which renders the CSS/logos from the ColorScheme admin on each request
# (ETag + no-cache), so admin changes show up on the next page load.
# LMS_ROOT_URL is the Python setting, so the dev (:8000) and prod URLs are
# both correct.
hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-lms-common-settings",
        """
# TitanEd brand theme (INDIGO_BRAND_THEME_SOURCE={{ INDIGO_BRAND_THEME_SOURCE }})
{% if INDIGO_BRAND_THEME_SOURCE == "live" %}
_TELS_BRAND_DIST = LMS_ROOT_URL + "/ui_configuration/theme"
{% elif INDIGO_BRAND_THEME_SOURCE == "development" %}
_TELS_BRAND_DIST = "{{ INDIGO_BRAND_THEME_DEVELOPMENT_URL.rstrip('/') }}"
{% else %}
_TELS_BRAND_DIST = "{{ INDIGO_BRAND_THEME_DEPLOYED_URL.rstrip('/') }}"
{% endif %}
FRONTEND_SITE_CONFIG.setdefault("commonAppConfig", {})
FRONTEND_SITE_CONFIG["commonAppConfig"]["INDIGO_ENABLE_DARK_TOGGLE"] = {{ INDIGO_ENABLE_DARK_TOGGLE }}
FRONTEND_SITE_CONFIG["commonAppConfig"]["INDIGO_FOOTER_NAV_LINKS"] = {{ INDIGO_FOOTER_NAV_LINKS }}
_TELS_PARAGON_CDN = "https://cdn.jsdelivr.net/npm/@openedx/paragon@{{ INDIGO_PARAGON_VERSION }}/dist"

# Legacy (frontend-platform) MFEs: `default` = full Paragon CSS,
# `brandOverride` = TitanEd tokens.
MFE_CONFIG["PARAGON_THEME_URLS"] = {
    "core": {
        "urls": {
            "default": _TELS_PARAGON_CDN + "/core.min.css",
            "brandOverride": _TELS_BRAND_DIST + "/core.min.css",
        },
    },
    "defaults": {"light": "light", "dark": "dark"},
    "variants": {
        "light": {
            "urls": {
                "default": _TELS_PARAGON_CDN + "/light.min.css",
                "brandOverride": _TELS_BRAND_DIST + "/light.min.css",
            },
        },
        # Paragon publishes no dark variant (its dist has only light.min.css), so the
        # brand dark stylesheet is both the base and the override, as in upstream Indigo.
        "dark": {
            "urls": {
                "default": _TELS_BRAND_DIST + "/dark.min.css",
                "brandOverride": _TELS_BRAND_DIST + "/dark.min.css",
            },
        },
    },
}
FRONTEND_SITE_CONFIG["commonAppConfig"]["PARAGON_THEME_URLS"] = MFE_CONFIG["PARAGON_THEME_URLS"]

# frontend-base sites bundle Paragon's base CSS, so `theme` only carries the
# brand override URLs (see mfe_config_api.views.translate_paragon_theme_urls).
FRONTEND_SITE_CONFIG["theme"] = {
    "core": {"url": _TELS_BRAND_DIST + "/core.min.css"},
    "defaults": {"light": "light", "dark": "dark"},
    "variants": {
        "light": {"url": _TELS_BRAND_DIST + "/light.min.css"},
        "dark": {"url": _TELS_BRAND_DIST + "/dark.min.css"},
    },
}
{% if INDIGO_BRAND_THEME_SOURCE == "live" %}
# Logos and favicon from the ColorScheme admin. LOGO_WHITE_URL (dark
# background variant) uses the footer logo upload, see control-panel's
# ui_configuration.views.footer_logo_redirect.
MFE_CONFIG["LOGO_URL"] = LMS_ROOT_URL + "/ui_configuration/logo"
MFE_CONFIG["LOGO_WHITE_URL"] = LMS_ROOT_URL + "/ui_configuration/footer-logo"
MFE_CONFIG["LOGO_TRADEMARK_URL"] = LMS_ROOT_URL + "/ui_configuration/logo"
MFE_CONFIG["FOOTER_LOGO_URL"] = LMS_ROOT_URL + "/ui_configuration/footer-logo"
MFE_CONFIG["FAVICON_URL"] = LMS_ROOT_URL + "/ui_configuration/favicon"
# Address, contact email, social links and copyright of the footer (IndigoFooter.jsx).
MFE_CONFIG["FOOTER_CONFIG_URL"] = LMS_ROOT_URL + "/ui_configuration/footer-config"
# Tells ThemedLogo/MobileViewHeader to use LOGO_URL/LOGO_WHITE_URL instead
# of the static Indigo logo images.
MFE_CONFIG["INDIGO_LIVE_BRANDING"] = True
FRONTEND_SITE_CONFIG["headerLogoImageUrl"] = MFE_CONFIG["LOGO_URL"]
for _tels_key in [
    "LOGO_WHITE_URL", "LOGO_TRADEMARK_URL", "FOOTER_LOGO_URL", "FAVICON_URL", "FOOTER_CONFIG_URL", "INDIGO_LIVE_BRANDING"
]:
    FRONTEND_SITE_CONFIG["commonAppConfig"][_tels_key] = MFE_CONFIG[_tels_key]
{% endif %}
""",
    )
)

# Install control-panel (custom_extensions: ui_configuration) from its private
# GitHub repo at INDIGO_CONTROL_PANEL_REPO_REF -- unless it is mounted from
# local disk, which tutor installs itself (pip install -e /mnt/control-panel).
hooks.Filters.ENV_PATCHES.add_item(
    (
        "openedx-dockerfile-post-python-requirements",
        """
{% if INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT and "control-panel" not in iter_mounted_directories(MOUNTS, "openedx")|list %}
{% if INDIGO_CONTROL_PANEL_REPO_TOKEN %}
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared $PIP_COMMAND install 'git+https://{{ INDIGO_CONTROL_PANEL_REPO_TOKEN }}@github.com/TitanEd/control-panel.git@{{ INDIGO_CONTROL_PANEL_REPO_REF }}'
{% else %}
RUN echo "ERROR: control-panel ({{ INDIGO_CONTROL_PANEL_REPO_REF }}) is installed from its private GitHub repo, but INDIGO_CONTROL_PANEL_REPO_TOKEN is not set. Fix: tutor config save --set INDIGO_CONTROL_PANEL_REPO_TOKEN=<fine-grained read-only PAT>, then rebuild. (Or mount a local checkout: tutor mounts add /path/to/control-panel; or skip it: --set INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT=false.)" && exit 1
{% endif %}
{% endif %}
""",  # noqa: E501
    )
)

# control-panel builds the live theme on the same tels-brand-openedx branch as
# the MFE brand package and the "deployed" theme URL (ui_configuration's
# UI_CONFIGURATION_UPSTREAM_BRAND_CSS_BASE, read by its theme views).
hooks.Filters.ENV_PATCHES.add_item(
    (
        "openedx-common-settings",
        """
UI_CONFIGURATION_UPSTREAM_BRAND_CSS_BASE = "{{ INDIGO_BRAND_THEME_DEPLOYED_URL.rstrip('/') }}"
""",
    )
)


@MFE_APPS.add()  # type: ignore
def _add_themed_logo(
    mfes: dict[str, MFE_ATTRS_TYPE],
) -> dict[str, MFE_ATTRS_TYPE]:
    for mfe in mfes:
        PLUGIN_SLOTS.add_item((str(mfe), *INDIGO_LOGO_SLOT))
        if str(mfe) not in indigo_styled_mfes and str(mfe) != "authoring":
            PLUGIN_SLOTS.add_item((str(mfe), *INDIGO_FOOTER_SLOT))

    return mfes


PLUGIN_SLOTS.add_items(
    [
        (
            "catalog",
            "org.openedx.frontend.catalog.home_page.course_card",
            """
        {
            op: PLUGIN_OPERATIONS.Hide,
            widgetId: 'default_contents',
        }
        """,
        ),
        (
            "catalog",
            "org.openedx.frontend.catalog.home_page.course_card",
            """
        {
            op: PLUGIN_OPERATIONS.Insert,
            widget: {
                id: 'indigo-catalog-home-course-card',
                type: DIRECT_PLUGIN,
                RenderWidget: (props) => (
                  <CourseCard {...props} />
                ),
            },
        },
        """,
        ),
        (
            "catalog",
            "org.openedx.frontend.catalog.course_catalog_page.data_table.course_card",
            """
        {
            op: PLUGIN_OPERATIONS.Hide,
            widgetId: 'default_contents',
        }
        """,
        ),
        (
            "catalog",
            "org.openedx.frontend.catalog.course_catalog_page.data_table.course_card",
            """
        {
            op: PLUGIN_OPERATIONS.Insert,
            widget: {
                id: 'indigo-catalog-course-card',
                type: DIRECT_PLUGIN,
                RenderWidget: (props) => (
                  <CourseCard {...props} />
                ),
            },
        },
        """,
        ),
    ]
)
