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
        # Site template used until an administrator picks one on the theme configuration page,
        # and when the LMS cannot be asked (see SITE_TEMPLATES below).
        "SITE_TEMPLATE_DEFAULT": "template-1",
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
        # Marketing URLs: the selected site template's marketing MFE, served at
        # ${MFE_HOST}/public (MARKETING_MFE_MOUNT; INDIGO_SITE_TEMPLATES adds the
        # origin in tutor dev). Override HOME_URL if your deployment mounts the
        # marketing MFE somewhere else, e.g.:
        #   tutor config save --set 'INDIGO_HOME_URL="https://learn.example.com"'
        # COURSES_URL: marketing MFE /public/courses (search submits here with ?q=).
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
        # The same server as seen from inside the LMS container (control-panel reads the
        # site template manifest dist/templates/index.json and proxies theme fonts from
        # it). Docker's bridge gateway, e.g. http://172.22.0.1:3000; empty = not reachable
        # (control-panel then lists the configured template ids without names).
        "BRAND_THEME_DEVELOPMENT_URL_INTERNAL": "",
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
# Site templates: the designs an administrator switches between on control-panel's
# theme configuration page ("Site template"). A template id is also the app id of
# its marketing MFE -- the fork of frontend-app-tels-public (home, catalog, about,
# contact, legal pages; the landing page of the platform, CATALOG_MICROFRONTEND_URL)
# served at /<id>. Each id matches a build of tels-brand-openedx
# (paragon/templates/<id>/, dist/templates/index.json) and the header / footer
# components registered in SiteHeader.jsx / SiteFooter.jsx. The choice is read at
# runtime (SITE_TEMPLATE_CONFIG_URL, SiteTemplate.jsx): no image build to switch.
# Add a template: brand layer + components + registry entries + one entry here
# (the marketing MFE is registered with tutor-mfe from this dict).
SITE_TEMPLATES: dict[str, dict[str, str | int]] = {
    "template-1": {
        "repository": "https://github.com/TitanEd/frontend-app-tels-public.git",
        "version": "native-plus-template-a",
        "port": 2024,
    },
    "template-2": {
        "repository": "https://github.com/TitanEd/frontend-app-tels-public.git",
        "version": "native-plus-template-b",
        "port": 2026,
    },
}

# One landing URL for every template: the marketing MFE of the *selected* template is served at
# MARKETING_MFE_MOUNT. Production (mfe image, Caddy): each template's build lives under
# /public/_t/<id>/ and /public/* answers with a small dispatcher page that loads the selected
# build (mfe-caddyfile patch below). tutor dev: every marketing dev server serves /public/*
# itself when its template is selected and proxies it to the selected template's dev server
# otherwise (mfe-webpack-dev-config patch below), so any marketing port shows the selection.
# The apps are built with PUBLIC_PATH=/public/ (router basename) for both.
MARKETING_MFE_MOUNT = "/public"
# kept for the slot / override loops below: every marketing MFE shares the one mount
MARKETING_MFE_MOUNTS: dict[str, str] = {template_id: MARKETING_MFE_MOUNT for template_id in SITE_TEMPLATES}

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
    *MARKETING_MFE_MOUNTS,
]

# The template headers and footers (CustomHeader, Template2Header, IndigoFooter,
# Template2Footer) render FontAwesome icons; only some MFEs depend on these
# packages themselves, so every styled image installs them with the brand.
_CHROME_NPM = " ".join(
    [
        "'@fortawesome/fontawesome-svg-core@1.2.36'",
        "'@fortawesome/free-brands-svg-icons@5.15.4'",
        "'@fortawesome/free-regular-svg-icons@5.15.4'",
        "'@fortawesome/free-solid-svg-icons@5.15.4'",
        "'@fortawesome/react-fontawesome@0.2.6'",
    ]
)

for mfe in indigo_styled_mfes:
    hooks.Filters.ENV_PATCHES.add_items(
        [
            (
                f"mfe-dockerfile-post-npm-install-{mfe}",
                f"""
RUN npm install '{{{{ INDIGO_BRAND_PACKAGE }}}}' {_CHROME_NPM}
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
# The marketing MFEs of SITE_TEMPLATES, registered with tutor-mfe (same MFE_APPS
# filter a standalone "add my MFE" plugin would use) so the app id, its
# brand/header/footer patches, its dev port and its template live in one place.
# A standalone plugin registering the same id with the same values is harmless.
# ---------------------------------------------------------------------------
FORKED_MFE_APPS: dict[str, dict[str, str | int]] = {
    template_id: {
        "repository": template["repository"],
        "port": template["port"],
        "version": template["version"],
    }
    for template_id, template in SITE_TEMPLATES.items()
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
#   marketing MFEs    empty HeaderSlot → header.v1 (insert only; no native default)
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
_MARKETING_HEADER_SLOTS: list[tuple[str, bool, str]] = [
    ("org.openedx.frontend.layout.header.v1", False, "custom_header"),
]

HEADER_REPLACEMENT_SLOTS: dict[str, list[tuple[str, bool, str]]] = {
    **{mfe: _MARKETING_HEADER_SLOTS for mfe in MARKETING_MFE_MOUNTS},
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
    already has a header (a marketing MFE's empty HeaderSlot must not Hide — there is
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
                    RenderWidget: SiteHeader,
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
# NOTE: HEADER_STYLED_MFES uses the real app ids (the SITE_TEMPLATES ids for the
# marketing MFEs), so no remapping is needed here.

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


_TELS_PORTS_JINJA = [
    "{% set tels_scheme = 'https' if ENABLE_HTTPS else 'http' %}",
    "{% set tels_ports = namespace(by_app={}) %}",
    "{% for tels_app, tels_mfe in iter_mfes() %}",
    "{% set tels_ports.by_app = dict(tels_ports.by_app, **{tels_app: tels_mfe['port']}) %}",
    "{% endfor %}",
]


def _marketing_host_jinja(with_port: str) -> str:
    """
    Jinja for the scheme + host (+ dev port) of the marketing URL. One URL for every template: without a web
    proxy (tutor dev) it is the dev port of the default template's marketing MFE -- every marketing dev server
    serves the selected template at /public (mfe-webpack-dev-config patch below).
    """
    return (
        "{{ tels_scheme }}://{{ MFE_HOST }}"
        "{% if " + with_port + " %}:"
        "{{ tels_ports.by_app.get(INDIGO_SITE_TEMPLATE_DEFAULT, '') }}"
        "{% endif %}"
    )


def _site_templates_mfe_config(with_port: str) -> str:
    """
    MFE_CONFIG['INDIGO_SITE_TEMPLATES']: id -> {mount, origin} for publicUrls.js / SiteHeader.jsx. The origin
    is "" behind the web proxy (same host: relative links) and host:port without it (tutor dev).
    """
    return "\n".join(
        _TELS_PORTS_JINJA
        + ["MFE_CONFIG['INDIGO_SITE_TEMPLATES'] = {"]
        + [
            f"    '{template_id}': {{'mount': '{MARKETING_MFE_MOUNTS[template_id]}', "
            "'origin': '{% if " + with_port + " %}" + _marketing_host_jinja(with_port) + "{% endif %}'},"
            for template_id in SITE_TEMPLATES
        ]
        + [
            "}",
            "MFE_CONFIG['INDIGO_SITE_TEMPLATE_DEFAULT'] = '{{ INDIGO_SITE_TEMPLATE_DEFAULT }}'",
            "",
        ]
    )


def _site_templates_lms_settings(with_port: str) -> str:
    """
    LMS settings for the landing page: TELS_SITE_TEMPLATES (id -> marketing_url), read by control-panel's
    SiteTemplateLandingMiddleware to send / and /courses to the selected template's marketing MFE, and
    CATALOG_MICROFRONTEND_URL / ENABLE_CATALOG_MICROFRONTEND for the platform's own catalog links.
    """
    return "\n".join(
        _TELS_PORTS_JINJA
        + ["TELS_SITE_TEMPLATES = {"]
        + [
            f"    '{template_id}': {{'marketing_url': '"
            + _marketing_host_jinja(with_port)
            + f"{MARKETING_MFE_MOUNT}'}},"
            for template_id in SITE_TEMPLATES
        ]
        + [
            "}",
            "TELS_SITE_TEMPLATE_DEFAULT = '{{ INDIGO_SITE_TEMPLATE_DEFAULT }}'",
            "ENABLE_CATALOG_MICROFRONTEND = True",
            "CATALOG_MICROFRONTEND_URL = TELS_SITE_TEMPLATES[TELS_SITE_TEMPLATE_DEFAULT]['marketing_url']",
            "",
        ]
    )


# Every marketing MFE: router basename /public (PUBLIC_PATH) and, in the production build, its
# assets under /public/_t/<id>/ so the builds of two templates can live behind one URL.
for _template_id in SITE_TEMPLATES:
    hooks.Filters.ENV_PATCHES.add_item(
        (
            f"mfe-dockerfile-pre-npm-build-{_template_id}",
            f"""
# Site template "{_template_id}": one landing URL for every template (SITE_TEMPLATES in tutor-tels-theme-plugins)
ENV PUBLIC_PATH='{MARKETING_MFE_MOUNT}/'
RUN printf "\\nmodule.exports.output = {{ ...module.exports.output, publicPath: '{MARKETING_MFE_MOUNT}/_t/{_template_id}/' }};\\n" \\
    >> webpack.prod-tutor.config.js
""",
        )
    )

# Production (mfe image): Caddy serves each template's build under /public/_t/<id>/ and answers
# /public/* with a dispatcher page that loads the build of the template selected on the theme
# configuration page (cookie first, then the LMS), so the URL stays /public/... whatever is selected.
_MARKETING_CADDY = "\n".join(
    [
        "# Site templates (tutor-tels-theme-plugins): one landing URL, the selected template's marketing MFE",
    ]
    + [
        line
        for template_id in SITE_TEMPLATES
        for line in [
            f"@tels_marketing_{template_id.replace('-', '_')} path {MARKETING_MFE_MOUNT}/_t/{template_id} "
            f"{MARKETING_MFE_MOUNT}/_t/{template_id}/*",
            f"handle @tels_marketing_{template_id.replace('-', '_')} {{",
            f"    uri strip_prefix {MARKETING_MFE_MOUNT}/_t/{template_id}",
            f"    root * /openedx/dist/{template_id}",
            "    try_files /{path} /index.html",
            "    file_server",
            "}",
        ]
    ]
    + [
        f"@tels_marketing path {MARKETING_MFE_MOUNT} {MARKETING_MFE_MOUNT}/*",
        "handle @tels_marketing {",
        '    header Content-Type "text/html; charset=utf-8"',
        '    header Cache-Control "no-store"',
        "    respond <<HTML",
        "    <!doctype html>",
        '    <html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
        "    <title>Loading…</title>",
        "    <script>",
        "    (async () => {",
        "      const base = '" + MARKETING_MFE_MOUNT + "/_t/';",
        "      const ids = " + repr(list(SITE_TEMPLATES)).replace("'", '"') + ";",
        "      const fallback = '{{ INDIGO_SITE_TEMPLATE_DEFAULT }}';",
        "      const cookie = /(?:^|; )tels-site-template=([a-z0-9-]+)/.exec(document.cookie);",
        "      let id = cookie && ids.includes(cookie[1]) ? cookie[1] : null;",
        "      if (!id) {",
        "        try {",
        "          const r = await fetch('{{ \"https\" if ENABLE_HTTPS else \"http\" }}://{{ LMS_HOST }}/ui_configuration/site-template');",
        "          if (r.ok) { const d = await r.json(); if (ids.includes(d.template)) { id = d.template; } }",
        "        } catch (e) { /* the default template below */ }",
        "      }",
        "      id = id || fallback;",
        "      const html = await (await fetch(base + id + '/index.html', { cache: 'no-store' })).text();",
        "      document.open(); document.write(html); document.close();",
        "    })();",
        "    </script></head><body></body></html>",
        "    HTML 200",
        "}",
        "",
    ]
)
hooks.Filters.ENV_PATCHES.add_item(("mfe-caddyfile", _MARKETING_CADDY))

# tutor dev: each marketing dev server serves /public/* for its own template and proxies it (and the
# webpack-dev-server websocket) to the selected template's dev server otherwise. The selection is
# polled from the LMS inside the compose network.
_MARKETING_DEV_PROXY = (
    """
// Site templates (tutor-tels-theme-plugins): /public/* on every marketing dev server shows the
// template selected on control-panel's theme configuration page, proxying to that template's
// dev server when it is another one.
const telsMarketingServers = {"""
    + ", ".join(f"'{template_id}': 'http://{template_id}:{template['port']}'" for template_id, template in SITE_TEMPLATES.items())
    + """};
if (telsMarketingServers[process.env.APP_ID]) {
  let telsSelected = process.env.APP_ID;
  const telsPoll = async () => {
    try {
      const response = await fetch('http://lms:8000/ui_configuration/site-template');
      if (response.ok) {
        const data = await response.json();
        if (telsMarketingServers[data.template]) { telsSelected = data.template; }
      }
    } catch (e) { /* keep the last answer */ }
  };
  telsPoll();
  setInterval(telsPoll, 5000).unref();
  const telsProxied = (pathname) => telsSelected !== process.env.APP_ID
    && (pathname === '"""
    + MARKETING_MFE_MOUNT
    + """' || pathname.startsWith('"""
    + MARKETING_MFE_MOUNT
    + """/'));
  const telsTarget = { target: telsMarketingServers[process.env.APP_ID], router: () => telsMarketingServers[telsSelected], changeOrigin: true };
  // The bundle middleware answers /public/* itself (it is this app's PUBLIC_PATH), so the proxy must run before it.
  const { createProxyMiddleware } = require('http-proxy-middleware');
  const telsHttpProxy = createProxyMiddleware(telsProxied, telsTarget);
  const telsSetup = module.exports.devServer.setupMiddlewares;
  module.exports.devServer.setupMiddlewares = (middlewares, devServer) => {
    const result = telsSetup ? telsSetup(middlewares, devServer) : middlewares;
    result.unshift({ name: 'tels-marketing-proxy', middleware: telsHttpProxy });
    return result;
  };
  // The webpack-dev-server websocket of the page follows the proxied app (hot reload of the selected template).
  const telsExisting = module.exports.devServer.proxy;
  module.exports.devServer.proxy = [
    ...(Array.isArray(telsExisting) ? telsExisting : Object.entries(telsExisting || {}).map(([context, options]) => ({ context: [context], ...options }))),
    { context: (pathname) => pathname === '/ws' && telsSelected !== process.env.APP_ID, ...telsTarget, ws: true },
  ];
}
"""
)
hooks.Filters.ENV_PATCHES.add_item(("mfe-webpack-dev-config", _MARKETING_DEV_PROXY))

# tutor dev containers carry PUBLIC_PATH=/<app id>/ from their image (Dockerfile ENV, before
# the pre-npm-build patch above sets /public/): rebuild the dev image of a marketing MFE
# after adding it to SITE_TEMPLATES (tutor images build <id>-dev).

hooks.Filters.ENV_PATCHES.add_items(
    [
        ("mfe-lms-common-settings", _site_templates_mfe_config("not ENABLE_WEB_PROXY")),
        ("openedx-lms-common-settings", _site_templates_lms_settings("not ENABLE_WEB_PROXY")),
        # tutor dev has no web proxy in front of the MFEs although ENABLE_WEB_PROXY
        # stays true: every MFE is on its own port, so the origins carry the port.
        ("openedx-lms-development-settings", _site_templates_mfe_config("true")),
        ("openedx-lms-development-settings", _site_templates_lms_settings("true")),
    ]
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
            RenderWidget: SiteFooter,
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
            RenderWidget: SiteFooter,
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
# The site template selected on control-panel's theme configuration page (SiteTemplate.jsx),
# and where the brand CSS comes from, so the MFE loads that template's stylesheets:
# "live" -- control-panel serves them; otherwise SiteTemplate.jsx rewrites the
# PARAGON_THEME_URLS links to <base>/templates/<id>/.
MFE_CONFIG["SITE_TEMPLATE_CONFIG_URL"] = LMS_ROOT_URL + "/ui_configuration/site-template"
MFE_CONFIG["INDIGO_BRAND_THEME_SOURCE"] = "{{ INDIGO_BRAND_THEME_SOURCE }}"
MFE_CONFIG["INDIGO_BRAND_THEME_BASE"] = _TELS_BRAND_DIST
for _tels_key in ["SITE_TEMPLATE_CONFIG_URL", "INDIGO_BRAND_THEME_SOURCE", "INDIGO_BRAND_THEME_BASE"]:
    FRONTEND_SITE_CONFIG["commonAppConfig"][_tels_key] = MFE_CONFIG[_tels_key]
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
{% if INDIGO_BRAND_THEME_SOURCE == "development" and INDIGO_BRAND_THEME_DEVELOPMENT_URL_INTERNAL %}
UI_CONFIGURATION_UPSTREAM_BRAND_CSS_BASE = "{{ INDIGO_BRAND_THEME_DEVELOPMENT_URL_INTERNAL.rstrip('/') }}"
{% else %}
UI_CONFIGURATION_UPSTREAM_BRAND_CSS_BASE = "{{ INDIGO_BRAND_THEME_DEPLOYED_URL.rstrip('/') }}"
{% endif %}
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
