Indigo, a cool blue theme for Open edX
======================================

Indigo is an elegant, customizable theme for `Open edX <https://openedx.org>`__.

.. image:: ./screenshots/01-landing-page.png
    :alt: Platform landing page

You can view the theme in action at https://sandbox.openedx.edly.io.

Installation
------------

Indigo was specially developed to be used with `Tutor <https://docs.tutor.edly.io>`__ (at least v14.0.0). If you have not installed Open edX with Tutor, then installation instructions will vary.

Install and enable Indigo plugin::

    tutor plugins install indigo
    tutor plugins enable indigo
    tutor local launch

The Indigo theme will be automatically enabled if you have not previously defined a theme. To override an existing theme, use the `settheme command <https://docs.tutor.edly.io/local.html#setting-a-new-theme>`__::

    tutor local do settheme indigo

Configuration
-------------

- ``INDIGO_WELCOME_MESSAGE`` (default: "The place for all your online learning")
- ``INDIGO_PRIMARY_COLOR`` (default: "#3b85ff")
- ``INDIGO_FOOTER_EXPLORE_LINKS`` / ``INDIGO_FOOTER_COMPANY_LINKS`` / ``INDIGO_FOOTER_SUPPORT_LINKS`` — marketing footer columns (``titleKey`` + ``url``); shown on every MFE
- ``INDIGO_FOOTER_CONTACT`` — email, web_url, web_label, address_lines
- ``INDIGO_FOOTER_SOCIAL_LINKS`` — social icons on every MFE footer
- ``INDIGO_FOOTER_NAV_LINKS`` — legacy flat list (kept for compatibility)
- ``INDIGO_ENABLE_DARK_TOGGLE`` (default: True)

Shared footer markup is ``IndigoFooter`` (``.tels-footer``); styles come from ``tels-brand-openedx`` design tokens. See ``docs/branding/header-footer-rules.md``.

The ``INDIGO_*`` settings listed above may be modified by running ``tutor config save --set INDIGO_...=...``. For instance, to clear social links, run::

    tutor config save --set "INDIGO_FOOTER_SOCIAL_LINKS=[]"

Or, to set the primary color to forest green, run::

    # Note: The nested quotes are needed in order to handle the hash (#) correctly.
    tutor config save --set 'INDIGO_PRIMARY_COLOR="#225522"'

Forked MFEs and custom Django plugin apps
------------------------------------------

This fork adds two more pieces of configuration on top of upstream Indigo, both in ``tutorindigo/plugin.py``, both designed so that adding the *next* forked MFE or custom Django app is a one-line dict entry — not a new Tutor plugin file or a hand-written Dockerfile patch.

Forked / custom MFEs (``FORKED_MFE_APPS``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some MFEs in this deployment aren't the stock ``openedx/frontend-app-*`` builds — they're TitanEd forks, or (for ``tels-public``) a brand-new MFE app entirely. They're all registered together via the ``FORKED_MFE_APPS`` dict near the top of ``tutorindigo/plugin.py``::

    FORKED_MFE_APPS: dict[str, dict[str, str | int]] = {
        "learning": {
            "repository": "https://github.com/TitanEd/frontend-app-learning.git",
            "port": 2000,
            "version": "native-tels/ulmo.4",
        },
        "tels-public": {
            "repository": "https://github.com/TitanEd/frontend-app-tels-public.git",
            "port": 2024,
            "version": "native-plus-template-a",
        },
    }

This is registered with ``tutor-mfe`` via ``tutormfe.hooks.MFE_APPS.add()``, exactly like the ``@MFE_APPS.add()`` pattern used by any standalone "add my MFE" Tutor plugin — the difference is that every forked/custom MFE lives in this one place instead of one plugin file each.

Each dict key is the MFE's app id:

- To **replace** a stock MFE with a TitanEd fork (like ``learning`` above), reuse its existing app id.
- To register a **brand-new** MFE (like ``tels-public``), pick a new id and use it *consistently* everywhere else that MFE is referenced in this file — Dockerfile ``ENV_PATCHES`` keys (``mfe-dockerfile-post-npm-install-<id>``), ``PLUGIN_SLOTS`` calls, ``indigo_styled_mfes``, ``HEADER_REPLACEMENT_SLOTS``, and any ``INDIGO_*_URL`` setting. A mismatched id silently no-ops the patch for that MFE instead of erroring — there is currently one such mismatch in this file (``tels-public`` vs ``public``) flagged in a comment next to ``FORKED_MFE_APPS``; check the rendered MFE Dockerfile (``env/plugins/mfe/build/mfe/Dockerfile``) if a patch doesn't seem to be landing.

To add another forked or custom MFE:

1. Add one entry to ``FORKED_MFE_APPS``: ``repository`` (git URL), ``version`` (branch/tag/commit), ``port`` (a free local dev port not used by another MFE).
2. ``tutor config save`` (re-renders the MFE build Dockerfile) then ``tutor images build mfe``.
3. If it should carry TitanEd branding, add its app id to ``indigo_styled_mfes`` so the brand CSS package installs at image-build time.
4. If it needs the shared custom header/footer, add it to ``HEADER_REPLACEMENT_SLOTS`` and the footer loop — see the "Header + footer overrides" comment block in ``plugin.py`` for which slot id(s) each MFE actually mounts (slot ids are not interchangeable between MFEs).

If you were previously registering a forked MFE from a separate, standalone Tutor plugin (e.g. one calling ``MFE_APPS.add()`` on its own), move its entry into ``FORKED_MFE_APPS`` here and disable that plugin (``tutor plugins disable <name>``) — leaving both enabled is harmless as long as the entries agree (identical values just get applied twice), but it's one fewer file to keep in sync.

Custom Django plugin apps (``CUSTOM_DJANGO_APPS``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TitanEd's own Django plugin apps for edx-platform — e.g. `control-panel <https://github.com/TitanEd/control-panel>`__ — are normally bind-mounted from local disk for development, so none of this applies day to day. On an environment with no local mount (UAT, staging, production), an app instead needs to be ``pip install``ed straight from its (private) GitHub repo when the ``openedx`` image is built. This is data-driven via the ``CUSTOM_DJANGO_APPS`` dict near the top of ``tutorindigo/plugin.py``::

    CUSTOM_DJANGO_APPS: dict[str, dict[str, str]] = {
        "CONTROL_PANEL": {
            "repo": "TitanEd/control-panel",
            "default_ref": "tels-template-1",
        },
    }

Each key generates three ``tutor config`` settings, prefixed ``INDIGO_<key>_``:

- ``INDIGO_<key>_INSTALL_FROM_GIT`` — bool, default ``false``. Set ``true`` **only** on environments that don't already have the package mounted from local disk.
- ``INDIGO_<key>_REPO_REF`` — branch/tag/commit to install; defaults to that entry's ``default_ref``.
- ``INDIGO_<key>_REPO_TOKEN`` — a GitHub Personal Access Token with **read-only** access to the repo (needed while it's private). No safe default; required whenever ``INSTALL_FROM_GIT`` is true.

For example, to install ``control-panel`` from git on a box with no local mount::

    tutor config save --set INDIGO_CONTROL_PANEL_INSTALL_FROM_GIT=true
    tutor config save --set INDIGO_CONTROL_PANEL_REPO_REF=tels-template-1
    tutor config save --set INDIGO_CONTROL_PANEL_REPO_TOKEN=<fine-grained, read-only, single-repo PAT>
    tutor images build openedx

Use a fine-grained PAT scoped to *only* that one repo, read-only — not a classic all-repos token — so a leak's blast radius is one private repo, not your whole GitHub org. These tokens end up in ``config.yml`` in plaintext, same as every other secret Tutor stores there (DB passwords, JWT keys, etc.); protect ``config.yml`` itself (file permissions, host access control, never commit it to git) rather than trying to avoid this storage mechanism.

To add your next custom Django plugin app, add one entry::

    CUSTOM_DJANGO_APPS: dict[str, dict[str, str]] = {
        "CONTROL_PANEL": {"repo": "TitanEd/control-panel", "default_ref": "tels-template-1"},
        "SOME_OTHER_APP": {"repo": "TitanEd/some-other-app", "default_ref": "main"},
    }

``tutor config save`` will then pick up the newly-generated ``INDIGO_SOME_OTHER_APP_*`` settings automatically, and the matching install step is added to the ``openedx`` Dockerfile — no new patch code required.

Theme Toggle Button
-------------------

The theme toggle button is enabled by default when Tutor Indigo is installed. The theme can be switched from light to dark and vice versa. To disable it, run::

    tutor config save --set INDIGO_ENABLE_DARK_TOGGLE=false
    tutor images build openedx
    tutor local start -d


Customization
-------------

This plugin can serve as a starting point to create your own themes. Just fork this repository and modify the files as you see fit.

You will have to start by installing indigo from source::

    git clone https://github.com/overhangio/tutor-indigo.git
    pip install -e ./tutor-indigo
    tutor plugins enable indigo

Any change you make to the theme can be viewed immediately in development mode (with `tutor dev ...` commands) after you run::

    tutor config save

To deploy your changes to production, you will have to rebuild the "openedx" Docker image and restart your containers::

    tutor images build openedx
    tutor local start -d

Changing the Styling in Sass files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To customize the theme stylesheets, modify the files in the ``tutorindigo/templates/indigo/lms/static/sass/`` and  ``tutorindigo/templates/indigo/cms/static/sass/`` directories. In particular, the ``_extras.scss`` files should contain most styling rules.


Changing the default logo and other images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The theme images are stored in `tutorindigo/templates/indigo/lms/static/images <https://github.com/overhangio/tutor-indigo/tree/release/tutorindigo/templates/indigo/lms/static/images>`__ for the LMS, and in `tutorindigo/templates/indigo/cms/static/images <https://github.com/overhangio/tutor-indigo/tree/release/tutorindigo/templates/indigo/cms/static/images>`__ for the CMS. To use custom images in your theme, just replace the files stored in these folders with your own.

Overriding the default "about", "contact", etc. static pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the ``/about`` and ``/contact`` pages contain a simple line of text: "This page left intentionally blank. Feel free to add your own content". This is of course unusable in production. In the following, we detail how to override just any of the static templates used in Open edX.

The static templates used by Open edX to render those pages are all stored in the `edx-platform/lms/templates/static_templates <https://github.com/edx/edx-platform/tree/open-release/sumac.master/lms/templates/static_templates>`__ folder. To override those templates, you should add your own in the following folder::

    ls tutorindigo/templates/indigo/lms/templates/static_templates"

For instance, edit the "donate.html" file in this directory. We can derive the content of this file from the contents of the `donate.html <https://github.com/edx/edx-platform/blob/open-release/sumac.master/lms/templates/static_templates/donate.html>`__ static template in edx-platform:

.. code-block:: mako

    <%page expression_filter="h"/>
    <%! from django.utils.translation import gettext as _ %>
    <%inherit file="../main.html" />

    <%block name="pagetitle">${_("Donate")}</%block>

    <main id="main" aria-label="Content" tabindex="-1">
        <section class="container about">
            <h1>
                <%block name="pageheader">${page_header or _("Donate")}</%block>
            </h1>
            <p>
                <%block name="pagecontent">Add a compelling message here, asking for donations.</%block>
            </p>
        </section>
    </main>

This new template will then be used to render the /donate url.

Troubleshooting
---------------

Can't override styles using Indigo Theme for MFEs
-------------------------------------------------

The indigo theme can’t override styles for MFEs directly. It overrides the styles for edx-platform. In case of MFEs, `@edx/brand <https://github.com/openedx/brand-openedx>`_ is used to override the styles. Customize the ``@edx/brand`` package to your preferences and include this customized package in `tutor-indigo` plugin. In this way, styles can be overidden::


    hooks.Filters.ENV_PATCHES.add_item((
                "mfe-dockerfile-post-npm-install",
                """
    RUN npm install '@edx/brand@npm:custom-brand-package'
    RUN npm install '@edx/brand@git+https://github.com/username/brand-openedx.git#custom-branch'
    """,
            ))


This Tutor plugin is maintained by Muhammad Faraz Maqsood and Hammad Yousaf from `Edly <https://edly.io>`__. Community support is available from the official `Open edX forum <https://discuss.openedx.org>`__. Do you need help with this plugin? See the `troubleshooting <https://docs.tutor.edly.io/troubleshooting.html>`__ section from the Tutor documentation.


License
-------

This work is licensed under the terms of the `GNU Affero General Public License (AGPL) <https://github.com/overhangio/tutor-indigo/blob/release/LICENSE.txt>`_.
