Indigo, a cool blue theme for Open edX
======================================

How-to guides (local setup, production setup, adding a site template): ``how-to/README.md``.

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
- ``INDIGO_FOOTER_NAV_LINKS`` (default: ``[{"title": "About", "url": "/about"}, {"title": "Contact", "url": "/contact"}]``)
- ``INDIGO_ENABLE_DARK_TOGGLE`` (default: True)

The ``INDIGO_*`` settings listed above may be modified by running ``tutor config save --set INDIGO_...=...``. For instance, to remove all links from the footer, run::

    tutor config save --set "INDIGO_FOOTER_NAV_LINKS=[]"

Or, to set the primary color to forest green, run::

    # Note: The nested quotes are needed in order to handle the hash (#) correctly.
    tutor config save --set 'INDIGO_PRIMARY_COLOR="#225522"'

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


Template-1 header, footer and marketing settings (TitanEd)
---------------------------------------------------------

Every MFE in ``indigo_styled_mfes`` (learner MFEs, Studio, the staff MFEs and the ``public``
marketing MFE) gets the shared ``CustomHeader`` (``.custom-header``) and the site footer
(``IndigoFooter``, ``.tels-footer``). The header is inserted on the host slot each MFE actually
mounts (see ``HEADER_REPLACEMENT_SLOTS`` in ``tutorindigo/plugin.py``; slot ids are not
interchangeable between header families). Discussions, Communications and ORA Grading do not
mount a header slot upstream, so their ``<Header />`` is wrapped in a ``PluginSlot`` at image
build (``LEARNING_HEADER_WRAP_FILES``). Styles come from the ``tels-brand-openedx`` design tokens
(``_header.scss`` / ``_footer.scss`` / ``_public.scss``); the plugin only ships markup and copy.

Settings (``tutor config save --set INDIGO_...=...``):

- ``INDIGO_ENABLE_LANGUAGE_MENU`` / ``INDIGO_SUPPORTED_LANGUAGES`` — header language menu (needs two or more languages to render)
- The template header keeps the native header controls (language menu and the ``INDIGO_ENABLE_DARK_TOGGLE`` dark-mode switch) at every viewport, next to the user menu or the hamburger button.
- The template header and footer apply to account, profile, learner-dashboard, gradebook, catalog, learning, discussions, communications, ora-grading and public. Authn has no site header, and authoring / admin-console keep the Studio header. The frontend-base ``site`` keeps its own shell header (styled to match) and gets the template footer through the compat slot.
- **Site templates** (``SITE_TEMPLATES`` in ``plugin.py``): an administrator picks the design of every app on the theme configuration page (``/theme/ui_configuration/#site-template``). Each template has a marketing MFE (a fork of ``frontend-app-tels-public``: landing page, catalog, about, contact and legal pages) registered under the template id: ``template-1`` is the TitanEd design (``CustomHeader`` / ``IndigoFooter``), ``template-2`` the Harvard-PLL design (``Template2Header`` / ``Template2Footer``). The marketing MFE of the *selected* template is served at one URL, ``/public`` (``MARKETING_MFE_MOUNT``): in production Caddy keeps each build under ``/public/_t/<id>/`` and answers ``/public/*`` with a dispatcher page that loads the selected one; in ``tutor dev`` every marketing dev server serves or proxies ``/public/*`` to the selected template's server. ``SiteHeader.jsx`` / ``SiteFooter.jsx`` render the selected header and footer on every MFE; ``SiteTemplate.jsx`` reads the choice from ``SITE_TEMPLATE_CONFIG_URL`` (control-panel) on every page load, keeps it in the ``tels-site-template`` cookie and, outside live branding, points the brand stylesheet links at that template's build (tels-brand-openedx ``dist/templates/<id>/``; in live mode control-panel serves it). The LMS landing page (``/``, ``/courses``) redirects to ``/public`` (``TELS_SITE_TEMPLATES`` + control-panel's ``SiteTemplateLandingMiddleware``; ``CATALOG_MICROFRONTEND_URL`` is the same URL). No restart or image build to switch. To add a template: a layer in tels-brand-openedx (``paragon/templates/<id>/``), a header and a footer component here, their entries in the two registries, one ``SITE_TEMPLATES`` entry (repository, version, port of its marketing MFE) and, for ``tutor dev``, ``tutor images build <id>-dev``. ``INDIGO_SITE_TEMPLATE_DEFAULT`` is the template used until one is selected; ``INDIGO_BRAND_THEME_DEVELOPMENT_URL_INTERNAL`` lets control-panel reach the development theme server from the LMS container.
- Marketing MFEs are registered from ``SITE_TEMPLATES``; nothing to add to a standalone ``MFE_APPS`` plugin.
- A clone of a marketing MFE for ``tutor dev`` must be named ``frontend-app-<id>`` (``tutor mounts add``), with ``PUBLIC_PATH='/public'`` and ``APP_ID='<id>'`` in its ``.env.development``.
- Local development: the ``mfe`` container serves image-built MFEs, so header and footer changes there need ``tutor images build mfe``. Dev containers that mount the rendered ``env.config.jsx`` (``tutor mounts add "<app>:$(tutor config printroot)/env/plugins/mfe/build/mfe/env.config.jsx:/openedx/app/env.config.jsx"``) pick them up on ``tutor config save`` and a container restart.
- ``INDIGO_HOME_URL`` / ``INDIGO_COURSES_URL`` / ``INDIGO_ABOUT_URL`` / ``INDIGO_CONTACT_URL`` / ``INDIGO_PRIVACY_URL`` / ``INDIGO_TERMS_URL`` — marketing URLs used by the header and footer; defaults point at the ``public`` MFE (``/public/...``)
- ``INDIGO_FOOTER_EXPLORE_LINKS`` / ``INDIGO_FOOTER_COMPANY_LINKS`` / ``INDIGO_FOOTER_SUPPORT_LINKS`` — footer columns (``titleKey`` + ``url``)
- ``INDIGO_FOOTER_CONTACT`` / ``INDIGO_FOOTER_SOCIAL_LINKS`` — contact block and social icons (the live theme's footer configuration page in control-panel takes precedence when it is set)
- ``INDIGO_FOOTER_NAV_LINKS`` — flat list kept for compatibility

Forked MFEs (``FORKED_MFE_APPS``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MFEs that are not stock ``openedx/frontend-app-*`` builds are registered in the ``FORKED_MFE_APPS``
dict of ``tutorindigo/plugin.py`` (``repository``, ``version``, ``port``), through ``tutormfe``'s
``MFE_APPS`` filter. The ``public`` marketing MFE (``frontend-app-tels-public``) is registered
there under the app id ``public``, which is also the id used in ``indigo_styled_mfes`` and
``HEADER_REPLACEMENT_SLOTS`` and the live path ``{MFE_HOST}/public/``. To add another one: add an
entry, ``tutor config save``, ``tutor images build mfe``; add its id to ``indigo_styled_mfes`` for
the brand package and to ``HEADER_REPLACEMENT_SLOTS`` for the shared header. A standalone plugin
that registers the same id with the same values is harmless and can be disabled.

Translations of the header and footer strings are merged into every styled MFE's
``src/i18n/messages/frontend-platform`` at image build (``TRANSLATION_SAFETY_NET_MFES``), so an
MFE whose own Makefile does not pull ``frontend-component-header`` still gets them.

License
-------

This work is licensed under the terms of the `GNU Affero General Public License (AGPL) <https://github.com/overhangio/tutor-indigo/blob/release/LICENSE.txt>`_.
