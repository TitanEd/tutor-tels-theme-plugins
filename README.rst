TitanEd theme plugin for Open edX (Indigo fork)
================================================

This is `TitanEd <https://github.com/TitanEd>`__'s fork of `Indigo
<https://github.com/overhangio/tutor-indigo>`__, an elegant, customizable
theme plugin for `Open edX <https://openedx.org>`__ / `Tutor
<https://docs.tutor.edly.io>`__, originally built by `Edly
<https://edly.io>`__. The pip package name, Tutor plugin name, and internal
Python package are still all literally ``indigo`` (unchanged from upstream,
see `Installation`_) — only the branding behavior described below has been
customized for TitanEd.

.. image:: ./screenshots/01-landing-page.png
    :alt: Platform landing page

**What this fork actually does today** is narrower than a full comprehensive
theme: it no longer ships its own LMS/CMS Sass/template tree at all (that
content was deliberately removed — see `Customization`_ below for where
theming actually lives now). What it *does* do:

1. Wires TitanEd's design tokens (colors, typography, fonts, logo, favicon)
   from `tels-brand-openedx <https://github.com/TitanEd/tels-brand-openedx>`__
   into every MFE, at both build time and runtime — see `Branded MFEs`_ and
   `TitanEd brand CSS ("live" theming)`_.
2. Installs `control-panel <https://github.com/TitanEd/control-panel>`__ (a
   private repo) into the ``openedx`` image, since the runtime branding
   above depends on its ``ui_configuration`` Django app being present — see
   `Deploying to a new environment (installing control-panel)`_.
3. Sets the ``theme_dir_name`` on the Tutor ``Site`` via an init task and a
   couple of small settings patches (``INDIGO_WELCOME_MESSAGE``,
   ``INDIGO_FOOTER_NAV_LINKS``, ``INDIGO_ENABLE_DARK_TOGGLE`` — legacy from
   upstream Indigo, still functional, see `Configuration`_).

Installation
------------

This fork isn't published to PyPI or Tutor's plugin index under a different
name — install it directly from source. The GitHub repo itself is public
(`github.com/TitanEd/tutor-tels-theme-plugins
<https://github.com/TitanEd/tutor-tels-theme-plugins>`__), no credentials
needed for this step::

    git clone https://github.com/TitanEd/tutor-tels-theme-plugins.git
    pip install -e ./tutor-tels-theme-plugins   # local dev: editable install
    # or, for a UAT/production host with no local checkout:
    #   pip install git+https://github.com/TitanEd/tutor-tels-theme-plugins.git@<branch-or-tag>
    tutor plugins enable indigo
    tutor local launch

The theme will be automatically enabled if you have not previously defined
one. To override an existing theme, use the `settheme command
<https://docs.tutor.edly.io/local.html#setting-a-new-theme>`__::

    tutor local do settheme indigo

**This is only step one of two for a new environment.** Enabling this
plugin does *not* by itself install ``control-panel`` — that needs its own
one-time per-environment setup because it's a private repo. See
`Deploying to a new environment (installing control-panel)`_ below; skipping
it leaves ``BRAND_THEME_SOURCE = "live"`` (the default, see next section)
pointing at endpoints that 404 forever.

Configuration
-------------

- ``INDIGO_WELCOME_MESSAGE`` (default: ``"The place for all your online learning"``)
- ``INDIGO_PRIMARY_COLOR`` (default: ``"#15376D"``) — legacy from upstream Indigo; **not** part of the
  live-theming path below, and not consumed by any current patch in this repo. If you're trying to change
  the site's brand color, you almost certainly want the ``ColorScheme.brand_color`` field in
  ``control-panel``'s Django admin instead — see `TitanEd brand CSS ("live" theming)`_.
- ``INDIGO_FOOTER_NAV_LINKS`` (default: a 7-item list — About Us, Blog, Donate, Terms of Service, Privacy
  Policy, Help, Contact Us, each a ``{"title": ..., "url": ...}`` dict)
- ``INDIGO_ENABLE_DARK_TOGGLE`` (default: ``True``)
- ``INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT`` (default: ``False``) — see `Deploying to a new environment
  (installing control-panel)`_
- ``INDIGO_CONTROL_PANEL_REPO_REF`` (default: ``"main"``) — same section
- ``INDIGO_CONTROL_PANEL_REPO_TOKEN`` (default: ``""``, no safe default) — same section

The ``INDIGO_*`` settings above may be modified by running ``tutor config save --set INDIGO_...=...``. For
instance, to remove all links from the footer, run::

    tutor config save --set "INDIGO_FOOTER_NAV_LINKS=[]"

TitanEd brand CSS ("live" theming)
-----------------------------------

Every MFE loads its Paragon design-system CSS from a config key called
``PARAGON_THEME_URLS``, resolved by ``frontend-platform`` into ``<link>``
tags at runtime — fetched fresh on every page load, not baked into the
MFE's JS bundle. ``tutorindigo/plugin.py`` builds this config, and can point
its ``brandOverride`` URLs at one of three sources, controlled by the
``BRAND_THEME_SOURCE`` constant near the bottom of ``plugin.py`` (this is a
plugin-source-code toggle, not a ``tutor config save --set`` setting):

.. list-table::
   :header-rows: 1

   * - ``BRAND_THEME_SOURCE``
     - brandOverride points at
     - When to use
   * - ``"development"``
     - ``http://localhost:3000``
     - Iterating on tokens locally in ``tels-brand-openedx`` — run
       ``npm run serve`` there first.
   * - ``"deployed"``
     - ``raw.githubusercontent.com/TitanEd/tels-brand-openedx`` (the
       ``native-tels-brand-openedx`` branch's built ``dist/``)
     - The original mechanism — every color/font/logo change needs a
       ``make build`` + ``git push`` to that branch, then a
       ``tutor config save`` on every deployment to pick it up.
   * - ``"live"`` (current default)
     - This deployment's own ``/ui_configuration/theme/<core|light|dark>.min.css``
       endpoint (served by ``control-panel``'s ``ui_configuration`` app)
     - Colors and fonts are editable live from Django admin — no
       ``make build``, no ``git push``, no rebuild. That endpoint itself
       still fetches the ``"deployed"`` URL above server-side and layers a
       live override on top, so typography/spacing/layout tokens still come
       from the git-based pipeline; only colors and the font-family choice
       are dynamic.

**"live" mode requires `control-panel`'s ``ui_configuration`` app to
actually be installed and reachable** — see the next section. If you ever
see 404s at ``/ui_configuration/theme/*.min.css`` or unstyled/default-color
MFEs, check that first, then check ``BRAND_THEME_SOURCE``.

Full detail on exactly which ``ColorScheme`` field controls which CSS
variable, including the reverse-engineered hover/active shade-ramp
generation, lives in `control-panel/ui_configuration/README.md
<https://github.com/TitanEd/control-panel/blob/main/ui_configuration/README.md>`__
— that's the doc an admin actually changing colors should read.

Logo, Footer Logo, and Favicon
-------------------------------

Separately from the CSS above, when ``BRAND_THEME_SOURCE = "live"``, this
plugin also points ``MFE_CONFIG``'s ``LOGO_URL``, ``LOGO_WHITE_URL``,
``LOGO_TRADEMARK_URL``, ``FOOTER_LOGO_URL``, and ``FAVICON_URL`` at
``control-panel``'s ``/ui_configuration/logo``, ``/footer-logo``, and
``/favicon`` endpoints (each a redirect to whatever's uploaded in Django
admin, or to the platform's stock default if nothing has been uploaded
yet). This is a separate, older Open edX config convention — plain URLs
``frontend-platform``'s header component reads at runtime — not something
this plugin invented.

This mostly supersedes (for the logo specifically) what `Branded MFEs`_
below does at build time — when both are active, whichever value the MFE's
header component actually prefers at runtime wins; this hasn't been
independently verified against every MFE's header implementation, so the
build-time ``@edx/brand`` install is kept as a safety net rather than
removed.

Branded MFEs
------------

The TitanEd design tokens (colors, typography, spacing, buttons, forms, links, dropdowns, and shared
header/footer chrome from `tels-brand-openedx <https://github.com/TitanEd/tels-brand-openedx>`__) apply to
every MFE at runtime via `TitanEd brand CSS ("live" theming)`_, regardless of the list below. What
``indigo_styled_mfes`` in ``tutorindigo/plugin.py`` controls is narrower: which MFEs get the TitanEd
``@edx/brand`` fork installed at **Docker build time** — i.e. which MFEs' JS bundles carry the TitanEd
logo/favicon/self-hosted-font assets as a fallback, independent of the runtime CSS/logo mechanisms above.
Currently::

    learning, learner-dashboard, profile, account, discussions, authoring, catalog,
    gradebook, ora-grading, communications, admin-console, authn

(``authn`` is wired separately, right after this list in ``plugin.py``.) The last four of the main list
(Gradebook, ORA Grading, Communications, Admin Console) are staff-only/internal tools, not learner-facing —
they're included so the brand is consistent everywhere staff work, not just on public pages. Header/footer
stay each MFE's native chrome for all of them (no ``PLUGIN_SLOTS`` overrides).

Changing this list requires a full ``tutor images build mfe`` to take effect (it's a Docker build-time
patch, unlike the CSS/logo endpoints above which take effect on the next page load with no rebuild).

Deploying to a new environment (installing control-panel)
-------------------------------------------------------------

Local dev installs ``control-panel`` via a **separate** Tutor plugin
(``tels_extensions_plugin.py``, not part of this repo) that bind-mounts a
local checkout and ``pip install -e``\ s it — that only works when the repo
happens to be checked out on the same host as the Docker build. A fresh
UAT/production host (an EC2 clone with no such local checkout) needs
``control-panel`` installed from GitHub instead — and it's a **private**
repo, so that install needs a credential.

Enabling this plugin (``tutor plugins enable indigo``) is *not* enough by
itself to install ``control-panel`` — that's a deliberate, explicit opt-in
(coupling it unconditionally to ``BRAND_THEME_SOURCE == "live"`` was tried
and broke local dev builds outright, since local dev has ``"live"`` mode on
*and* already gets ``control-panel`` via the mount above). One-time setup,
per environment that needs the git-based install::

    tutor config save --set INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT=true
    tutor config save --set INDIGO_CONTROL_PANEL_REPO_TOKEN=<your-github-token>
    tutor config save --set INDIGO_CONTROL_PANEL_REPO_REF=<branch-or-tag>   # optional, defaults to "main"
    tutor images build openedx mfe
    tutor local start -d

After that, every future ``tutor config save && tutor images build openedx``
picks up whatever ``INDIGO_CONTROL_PANEL_REPO_REF`` currently points at —
no further manual steps.

**Getting a token.** Use a **fine-grained** GitHub Personal Access Token,
scoped to **read-only** access on **only** the ``TitanEd/control-panel``
repository — never a classic all-repos token. If it ever leaks, the blast
radius is one private repo, not your whole GitHub org.

**Where the token ends up, and why that matters.** ``INDIGO_CONTROL_PANEL_REPO_TOKEN`` is stored in Tutor's
``config.yml`` in plaintext — the same place every other secret in a Tutor deployment already lives
(database passwords, JWT signing keys, etc.). Protect ``config.yml`` itself: restrict its file permissions,
control who has shell access to the host, and never commit it to git. Additionally — because the actual
install happens as a plain Docker ``RUN`` (not a `BuildKit secret mount
<https://docs.docker.com/build/building/secrets/>`__), **the resolved command, including the token, is
recorded in the built image's layer history** (visible via ``docker history --no-trunc``) — a larger
exposure than "the token sits in a file," since anyone who can pull or inspect that image can extract it
too, not only whoever can read ``config.yml``. Given that:

- Rotate the token periodically.
- Never run ``tutor images build --cache-to-registry`` for the ``openedx`` image — that would push the
  token-containing layer to a shared registry cache.
- If your threat model needs a zero-token-at-rest guarantee instead, replace the
  ``openedx-dockerfile-post-python-requirements`` patch in ``plugin.py`` with a BuildKit secret mount and
  pass the token per-build with ``tutor images build openedx -d "--secret id=github_token,env=GITHUB_TOKEN"``
  — this trades single-click automation (the token can no longer live in ``config.yml``; it must be
  supplied on every build invocation) for that stronger guarantee. Not implemented here; this was a
  deliberate choice in favor of convenience, documented so it's easy to revisit later.

**If ``INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT`` is ``true`` but the token is empty**, the ``openedx`` image
build fails loudly with an actionable error message (rather than silently skipping the install and leaving
``ui_configuration`` 404ing until someone notices much later).

Theme Toggle Button
--------------------

The theme toggle button is enabled by default when this plugin is installed. The theme can be switched from
light to dark and vice versa. To disable it, run::

    tutor config save --set INDIGO_ENABLE_DARK_TOGGLE=false
    tutor images build openedx
    tutor local start -d

Customization
-------------

**Where theming actually lives now** (this changed from upstream Indigo — read this before looking for a
file that no longer exists in this repo):

.. list-table::
   :header-rows: 1

   * - What you want to change
     - Where
   * - Colors, font-family, logo, footer logo, favicon (live, no rebuild)
     - ``control-panel``'s Django admin — `ColorScheme
       <https://github.com/TitanEd/control-panel/blob/main/ui_configuration/README.md>`__
   * - Typography sizing, spacing, page width, component-level SCSS overrides (colors excepted)
     - `tels-brand-openedx <https://github.com/TitanEd/tels-brand-openedx>`__ — see its ``CONTROLS.md``
   * - LMS/CMS server-rendered Django templates and Sass (course pages, dashboards, emails, etc.)
     - The separate ``tels-theme`` comprehensive theme repo (**not** this repo — see below)
   * - Which MFEs get the TitanEd logo/favicon baked in at build time
     - ``indigo_styled_mfes`` in ``tutorindigo/plugin.py`` — see `Branded MFEs`_
   * - Welcome message, footer nav links, dark-mode toggle
     - ``INDIGO_*`` settings — see `Configuration`_

**This repo's own comprehensive-theme content (Sass, templates, images under
``tutorindigo/templates/indigo/lms/`` and ``.../cms/``) was deliberately
removed** — ``templates/indigo/`` now contains only ``tasks/init.sh``
(theme-name assignment). If you're looking at an older guide (including
upstream Indigo's own README, which this file used to closely mirror)
describing how to edit
``tutorindigo/templates/indigo/lms/static/sass/_extras.scss``, override
``.../lms/templates/static_templates/donate.html``, or replace images under
``.../lms/static/images/`` — none of those paths exist in this repo
anymore. Use the table above instead.

If you're building a *new*, unrelated theme from this plugin as a starting
point rather than working with TitanEd's setup, you'll likely want to
restore a real theme tree under ``templates/indigo/`` first (`upstream
Indigo's history
<https://github.com/overhangio/tutor-indigo/tree/release/tutorindigo/templates/indigo>`__
is a reasonable base to fork from), since this fork's current state assumes
theming happens in ``tels-brand-openedx``/``tels-theme``/``control-panel``
instead.

Troubleshooting
----------------

Can't override styles using this theme for MFEs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This theme can't override styles for MFEs directly by itself — it overrides styles for edx-platform (the
LMS/CMS server-rendered pages). For MFEs, styling comes through `@edx/brand
<https://github.com/openedx/brand-openedx>`__, installed at Docker build time, plus — for this fork — the
runtime CSS/logo mechanisms described in `TitanEd brand CSS ("live" theming)`_ and
`Logo, Footer Logo, and Favicon`_ above.

The actual working pattern in this repo, per MFE (see ``indigo_styled_mfes`` in ``plugin.py`` for the
full list this is applied to)::

    for mfe in indigo_styled_mfes:
        hooks.Filters.ENV_PATCHES.add_items([
            (
                f"mfe-dockerfile-post-npm-install-{mfe}",
                "RUN npm install '@edx/brand@github:@TitanEd/tels-brand-openedx#native-tels-brand-openedx'",
            ),
        ])

If you're forking this further for a different brand package, replace the ``@edx/brand@github:...`` target
with your own npm package or git branch, e.g. ``@edx/brand@npm:custom-brand-package`` or
``@edx/brand@git+https://github.com/username/brand-openedx.git#custom-branch``.

Community support is available from the official `Open edX forum <https://discuss.openedx.org>`__. See the
`troubleshooting <https://docs.tutor.edly.io/troubleshooting.html>`__ section from the Tutor documentation
for issues unrelated to this fork's own customizations.

Fork notice
-----------

This plugin was originally created as **Indigo** by Muhammad Faraz Maqsood and Hammad Yousaf at `Edly
<https://edly.io>`__, and is licensed under the terms of the `GNU Affero General Public License (AGPL)
<https://github.com/overhangio/tutor-indigo/blob/release/LICENSE.txt>`__. TitanEd maintains this fork
(`github.com/TitanEd/tutor-tels-theme-plugins <https://github.com/TitanEd/tutor-tels-theme-plugins>`__),
adding the TitanEd branding/``control-panel`` integration described above; it continues to track upstream
Indigo releases where practical. See upstream at `github.com/overhangio/tutor-indigo
<https://github.com/overhangio/tutor-indigo>`__ for the original, unmodified theme.

License
-------

This work is licensed under the terms of the `GNU Affero General Public License (AGPL)
<https://github.com/overhangio/tutor-indigo/blob/release/LICENSE.txt>`__.
