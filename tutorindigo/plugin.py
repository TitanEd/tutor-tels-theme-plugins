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
        # TitanEd brand CSS source for the MFEs (PARAGON_THEME_URLS):
        #   "live"        -> control-panel's ui_configuration app
        #                    (LMS_ROOT_URL/ui_configuration/theme/*). Changes made
        #                    in /admin/ui_configuration/colorscheme/ apply on the
        #                    next page load, no restart or rebuild needed.
        #   "deployed"    -> tels-brand-openedx dist/ on GitHub
        #   "development" -> local tels-brand-openedx `npm run serve`
        #   "indigo"      -> upstream Indigo (edly-io brand-openedx), unchanged
        #   tutor config save --set INDIGO_BRAND_THEME_SOURCE=live
        "BRAND_THEME_SOURCE": "live",
        "BRAND_THEME_DEVELOPMENT_URL": "http://localhost:3000",
        "BRAND_THEME_DEPLOYED_URL": (
            "https://raw.githubusercontent.com/TitanEd/tels-brand-openedx/"
            "refs/heads/native-tels-brand-openedx/dist"
        ),
        # Full Paragon CSS used as the `default` URL next to `brandOverride`
        # for legacy (frontend-platform) MFEs.
        "PARAGON_VERSION": "23.14.9",
        # npm package installed as @edx/brand in the MFE image (build time).
        # TitanEd brand: tutor config save --set
        #   INDIGO_BRAND_PACKAGE="@edx/brand@github:@TitanEd/tels-brand-openedx#native-tels-brand-openedx"
        "BRAND_PACKAGE": "@edx/brand@github:@edly-io/brand-openedx#indigo-3.1.0",
        # CONTROL_PANEL_INSTALL_FROM_GIT: set to true ONLY on environments
        # that don't already have control-panel mounted from local disk --
        # i.e. UAT/prod, never local dev:
        #   tutor config save --set INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT=true
        "CONTROL_PANEL_INSTALL_FROM_GIT": False,
        # CONTROL_PANEL_REPO_REF: which branch/tag/commit of control-panel
        # to install, e.g.
        #   tutor config save --set INDIGO_CONTROL_PANEL_REPO_REF=uat
        "CONTROL_PANEL_REPO_REF": "main",
        # CONTROL_PANEL_REPO_TOKEN: a fine-grained, read-only GitHub PAT scoped
        # to TitanEd/control-panel only (private repo). MUST be set per
        # environment; it ends up in config.yml and in the image build history:
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

for mfe in indigo_styled_mfes:
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

paragon_theme_urls = {
    "variants": {
        "light": {
            "urls": {
                "default": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/verawood/indigo/dist/light.min.css",
                "brandOverride": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/verawood/indigo/dist/light.min.css",
            },
        },
        "dark": {
            "urls": {
                "default": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/verawood/indigo/dist/dark.min.css",
                "brandOverride": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/verawood/indigo/dist/dark.min.css",
            }
        },
    }
}

frontend_base_theme = {
    "core": {
        "url": "https://cdn.jsdelivr.net/gh/edly-io/brand-openedx@refs/heads/verawood/indigo/dist/core.min.css",
    },
    "defaults": {
        "light": "light",
        "dark": "dark",
    },
    "variants": {
        "light": {
            "url": "https://cdn.jsdelivr.net/gh/edly-io/brand-openedx@refs/heads/verawood/indigo/dist/light.min.css",
        },
        "dark": {
            "url": "https://cdn.jsdelivr.net/gh/edly-io/brand-openedx@refs/heads/verawood/indigo/dist/dark.min.css",
        },
    },
}

hooks.Filters.CONFIG_DEFAULTS.add_item(("PARAGON_THEME_URLS", paragon_theme_urls))

hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-lms-common-settings",
        """
MFE_CONFIG["PARAGON_THEME_URLS"] = {{ PARAGON_THEME_URLS }}
FRONTEND_SITE_CONFIG.setdefault("commonAppConfig", {})
FRONTEND_SITE_CONFIG["theme"] = """
        + json.dumps(frontend_base_theme)
        + """
FRONTEND_SITE_CONFIG["commonAppConfig"]["PARAGON_THEME_URLS"] = {{ PARAGON_THEME_URLS }}
FRONTEND_SITE_CONFIG["commonAppConfig"][
    "INDIGO_ENABLE_DARK_TOGGLE"
] = {{ INDIGO_ENABLE_DARK_TOGGLE }}
FRONTEND_SITE_CONFIG["commonAppConfig"][
    "INDIGO_FOOTER_NAV_LINKS"
] = {{ INDIGO_FOOTER_NAV_LINKS }}
""",
    )
)

# TitanEd brand CSS, logos and favicon. Rendered after the Indigo settings
# above, so it replaces them unless INDIGO_BRAND_THEME_SOURCE is "indigo".
# In "live" mode every URL points at control-panel's ui_configuration app,
# which renders the CSS/logos from the ColorScheme admin on each request
# (ETag + no-cache), so admin changes show up on the next page load.
# LMS_ROOT_URL is the Python setting, so the dev (:8000) and prod URLs are
# both correct.
hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-lms-common-settings",
        """
{% if INDIGO_BRAND_THEME_SOURCE in ["live", "deployed", "development"] %}
# TitanEd brand theme (INDIGO_BRAND_THEME_SOURCE={{ INDIGO_BRAND_THEME_SOURCE }})
{% if INDIGO_BRAND_THEME_SOURCE == "live" %}
_TELS_BRAND_DIST = LMS_ROOT_URL + "/ui_configuration/theme"
{% elif INDIGO_BRAND_THEME_SOURCE == "deployed" %}
_TELS_BRAND_DIST = "{{ INDIGO_BRAND_THEME_DEPLOYED_URL.rstrip('/') }}"
{% else %}
_TELS_BRAND_DIST = "{{ INDIGO_BRAND_THEME_DEVELOPMENT_URL.rstrip('/') }}"
{% endif %}
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
        "dark": {
            "urls": {
                "default": _TELS_PARAGON_CDN + "/dark.min.css",
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
# Tells ThemedLogo/MobileViewHeader to use LOGO_URL/LOGO_WHITE_URL instead
# of the static Indigo logo images.
MFE_CONFIG["INDIGO_LIVE_BRANDING"] = True
FRONTEND_SITE_CONFIG["headerLogoImageUrl"] = MFE_CONFIG["LOGO_URL"]
for _tels_key in ["LOGO_WHITE_URL", "LOGO_TRADEMARK_URL", "FOOTER_LOGO_URL", "FAVICON_URL", "INDIGO_LIVE_BRANDING"]:
    FRONTEND_SITE_CONFIG["commonAppConfig"][_tels_key] = MFE_CONFIG[_tels_key]
{% endif %}
{% endif %}
""",
    )
)

# Install control-panel (custom_extensions: ui_configuration, course_metadata,
# ...) from its private GitHub repo. Only for environments that don't mount a
# local checkout (UAT/prod), see the INDIGO_CONTROL_PANEL_* settings.
hooks.Filters.ENV_PATCHES.add_item(
    (
        "openedx-dockerfile-post-python-requirements",
        """
{% if INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT %}
{% if INDIGO_CONTROL_PANEL_REPO_TOKEN %}
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared $PIP_COMMAND install 'git+https://{{ INDIGO_CONTROL_PANEL_REPO_TOKEN }}@github.com/TitanEd/control-panel.git@{{ INDIGO_CONTROL_PANEL_REPO_REF }}'
{% else %}
RUN echo "ERROR: INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT is true but INDIGO_CONTROL_PANEL_REPO_TOKEN is not set. Fix: tutor config save --set INDIGO_CONTROL_PANEL_REPO_TOKEN=<fine-grained read-only PAT>, then rebuild." && exit 1
{% endif %}
{% endif %}
""",  # noqa: E501
    )
)


@MFE_APPS.add()  # type: ignore
def _add_themed_logo(
    mfes: dict[str, MFE_ATTRS_TYPE],
) -> dict[str, MFE_ATTRS_TYPE]:
    for mfe in mfes:
        PLUGIN_SLOTS.add_item((str(mfe), *INDIGO_LOGO_SLOT))

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
