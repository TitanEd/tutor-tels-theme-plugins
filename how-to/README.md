# How-to guides

Step-by-step guides for the TELS theme stack: this Tutor plugin (`indigo`), the brand package
[tels-brand-openedx](https://github.com/TitanEd/tels-brand-openedx), the admin app
[control-panel](https://github.com/TitanEd/control-panel) (`ui_configuration`) and the marketing MFE
[frontend-app-tels-public](https://github.com/TitanEd/frontend-app-tels-public).

| Guide | When |
|---|---|
| [01 — Local development setup](01-local-development-setup.md) | Run the whole stack on a laptop with `tutor dev`, hot reload for brand CSS and MFE code |
| [02 — Production setup](02-production-setup.md) | Configure, build and operate it on a server (`tutor local` / Kubernetes) |
| [03 — Add a new site template](03-add-a-new-site-template.md) | Ship a `template-3`: marketing MFE branch, brand layer, header and footer components, registration |

## How the pieces fit

```
administrator ──▶ /theme/ui_configuration/light#site-template  (control-panel)
                      │ stores SiteTemplateConfiguration
                      ▼
   GET /ui_configuration/site-template  ──▶  every MFE (SiteTemplate.jsx, cookie tels-site-template)
          │                                      ├─ SiteHeader / SiteFooter render the template's components
          │                                      └─ stylesheets: dist/templates/<id>/ of tels-brand-openedx
          ├─▶ LMS landing (/, /courses) ──302──▶ MFE_HOST/public   (SiteTemplateLandingMiddleware)
          └─▶ /public/* serves the selected template's marketing MFE
                 prod: Caddy dispatcher + /public/_t/<id>/      dev: each marketing dev server proxies
```

- A **site template** is an id (`template-1`, `template-2`, …) that names, at the same time: a marketing MFE
  (a branch of frontend-app-tels-public, registered in `SITE_TEMPLATES`), a brand layer
  (`tels-brand-openedx/paragon/templates/<id>/`, built to `dist/templates/<id>/`) and a header and footer
  component pair in this plugin (`SiteHeader.jsx` / `SiteFooter.jsx` registries).
- Switching templates never needs a restart or an image build. Adding a template does (once).
