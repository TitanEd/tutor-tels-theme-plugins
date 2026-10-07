// Site template in use (control-panel theme configuration page, "Site template"): which header and footer
// every MFE renders, which marketing MFE its links point to, and -- outside live branding -- which build of
// the brand CSS it loads. Runs once per page load, at module evaluation, before the app initialises
// (mfe-env-config-buildtime-definitions).
//
// Source of truth: SITE_TEMPLATE_CONFIG_URL (LMS /ui_configuration/site-template) -> {template, path}.
// The last answer is kept in the `tels-site-template` cookie ("<id>|<path>"), shared by every host of the
// site, so the first render already uses it; the fetch then confirms or corrects it (components re-render
// through useSiteTemplate). Without a URL the default INDIGO_SITE_TEMPLATE_DEFAULT applies.
//
// Stylesheets: with INDIGO_BRAND_THEME_SOURCE "live", control-panel serves the selected template's CSS at the
// PARAGON_THEME_URLS it hands out, nothing to do here. With any other source (development: the brand repo's
// own server; deployed: the published dist/), the URLs point at the shared base <base>/<variant>.min.css and
// this module rewrites every brand stylesheet link to <base>/<path>/<variant>.min.css as frontend-platform
// inserts it, so the page never paints with another template's chrome.
const telsSiteTemplateCookie = 'tels-site-template';
const telsSiteTemplateListeners = new Set();

const telsReadSiteTemplateCookie = () => {
  try {
    const match = document.cookie.match(new RegExp(`(?:^|; )${telsSiteTemplateCookie}=([a-z0-9-]+)(?:%7C|\\|)?([A-Za-z0-9%/_-]*)`));
    if (!match) {
      return { template: null, path: null };
    }
    return { template: match[1], path: match[2] ? decodeURIComponent(match[2]) : '' };
  } catch (e) {
    return { template: null, path: null };
  }
};

const telsWriteSiteTemplateCookie = (template, templatePath) => {
  try {
    const host = window.location.hostname;
    const parts = host.split('.');
    const domain = parts.length > 2 ? `.${parts.slice(-2).join('.')}` : host;
    const value = `${template}|${encodeURIComponent(templatePath || '')}`;
    document.cookie = `${telsSiteTemplateCookie}=${value}; domain=${domain}; path=/; max-age=${90 * 24 * 3600}; SameSite=Lax`;
  } catch (e) {
    // no cookie access (privacy mode): the fetch result still applies to this page
  }
};

window.telsSiteTemplate = { ...telsReadSiteTemplateCookie(), loaded: false };

const telsSetSiteTemplate = (template, templatePath, loaded) => {
  const changed = window.telsSiteTemplate.template !== template || window.telsSiteTemplate.path !== templatePath;
  window.telsSiteTemplate = { ...window.telsSiteTemplate, template, path: templatePath, loaded };
  if (changed || loaded) {
    telsSiteTemplateListeners.forEach((listener) => listener(window.telsSiteTemplate));
  }
};

// --- Brand stylesheets of the selected template (every source but "live") ---
const telsBrandVariant = /\/(core|light|dark)\.min\.css(\?.*)?$/;
let telsBrandBase = null; // INDIGO_BRAND_THEME_BASE once the config is known

const telsTemplateStylesheetHref = (href) => {
  const templatePath = window.telsSiteTemplate.path;
  if (!telsBrandBase || !templatePath || !href || !href.startsWith(telsBrandBase)) {
    return null;
  }
  const match = telsBrandVariant.exec(href);
  if (!match || href.includes(`/${templatePath}/`)) {
    return null;
  }
  return `${telsBrandBase}/${templatePath}/${match[1]}.min.css${match[2] || ''}`;
};

const telsRetargetBrandLinks = () => {
  document.querySelectorAll('link[rel~="stylesheet"][href], link[rel~="alternate"][href]').forEach((link) => {
    const next = telsTemplateStylesheetHref(link.getAttribute('href'));
    if (next) {
      link.setAttribute('href', next);
    }
  });
};

if (typeof MutationObserver !== 'undefined') {
  const telsLinkObserver = new MutationObserver((mutations) => {
    if (mutations.some((m) => Array.from(m.addedNodes).some((n) => n.nodeType === 1))) {
      telsRetargetBrandLinks();
    }
  });
  const telsObserveHead = () => telsLinkObserver.observe(document.head || document.documentElement, { childList: true, subtree: true });
  if (document.head) {
    telsObserveHead();
  } else {
    document.addEventListener('DOMContentLoaded', telsObserveHead, { once: true });
  }
}

// The config is not available at module evaluation; the first component to mount triggers the fetch.
let telsSiteTemplateRequest = null;
const telsLoadSiteTemplate = (config) => {
  if (config.INDIGO_BRAND_THEME_SOURCE && config.INDIGO_BRAND_THEME_SOURCE !== 'live' && config.INDIGO_BRAND_THEME_BASE) {
    telsBrandBase = String(config.INDIGO_BRAND_THEME_BASE).replace(/\/$/, '');
    telsRetargetBrandLinks();
  }
  if (telsSiteTemplateRequest) {
    return telsSiteTemplateRequest;
  }
  const fallback = config.INDIGO_SITE_TEMPLATE_DEFAULT || 'template-1';
  const url = config.SITE_TEMPLATE_CONFIG_URL;
  if (!url) {
    telsSiteTemplateRequest = Promise.resolve(fallback);
    telsSetSiteTemplate(fallback, window.telsSiteTemplate.path || '', true);
    return telsSiteTemplateRequest;
  }
  telsSiteTemplateRequest = fetch(url, { credentials: 'omit' })
    .then((response) => (response.ok ? response.json() : null))
    .then((data) => {
      const template = (data && data.template) || window.telsSiteTemplate.template || fallback;
      const templatePath = data && typeof data.path === 'string' ? data.path : (window.telsSiteTemplate.path || '');
      telsWriteSiteTemplateCookie(template, templatePath);
      telsSetSiteTemplate(template, templatePath, true);
      telsRetargetBrandLinks();
      return template;
    })
    .catch(() => {
      const template = window.telsSiteTemplate.template || fallback;
      telsSetSiteTemplate(template, window.telsSiteTemplate.path || '', true);
      return template;
    });
  return telsSiteTemplateRequest;
};

/** The site template id in use, re-rendering when the LMS answer differs from the cookie. */
const useSiteTemplate = () => {
  const config = getConfig();
  const fallback = config.INDIGO_SITE_TEMPLATE_DEFAULT || 'template-1';
  const [state, setState] = useState(window.telsSiteTemplate);
  useEffect(() => {
    telsSiteTemplateListeners.add(setState);
    telsLoadSiteTemplate(config);
    return () => telsSiteTemplateListeners.delete(setState);
  }, []);
  return { template: state.template || fallback, known: Boolean(state.template) || state.loaded };
};
