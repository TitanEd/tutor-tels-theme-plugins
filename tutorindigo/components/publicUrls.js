/** The one mount of the marketing MFEs (MARKETING_MFE_MOUNT in plugin.py): the selected template is served there. */
const PUBLIC_MFE_MOUNT = '/public';

const ROUTE_CONFIG_KEYS = {
  '/': 'INDIGO_HOME_URL',
  '/home': 'INDIGO_HOME_URL',
  '/courses': 'INDIGO_COURSES_URL',
  '/about': 'INDIGO_ABOUT_URL',
  '/contact': 'INDIGO_CONTACT_URL',
  '/privacy': 'INDIGO_PRIVACY_URL',
  '/terms': 'INDIGO_TERMS_URL',
};

/** Marketing route path per header/footer urlKey. */
const PUBLIC_ROUTE_BY_KEY = {
  home: '/',
  courses: '/courses',
  about: '/about',
  contact: '/contact',
  privacy: '/privacy',
  terms: '/terms',
};

function isSiteRoot(value) {
  return !value || value === '/' || value === '';
}

/**
 * The marketing MFE of the site template in use (SiteTemplate.jsx: the template selected on
 * control-panel's theme configuration page), from INDIGO_SITE_TEMPLATES: {mount, origin}, or null.
 */
function getSiteTemplateMarketing(config) {
  const selected = typeof window !== 'undefined' && window.telsSiteTemplate ? window.telsSiteTemplate.template : null;
  const templates = (config && config.INDIGO_SITE_TEMPLATES) || {};
  const entry = (selected && templates[selected]) || templates[config && config.INDIGO_SITE_TEMPLATE_DEFAULT] || null;
  if (!entry || !entry.mount) {
    return null;
  }
  if (typeof window !== 'undefined' && window.telsSiteTemplate) {
    // Remembered for the helpers that get no config (toPublicAppPath, collapseDoubledMount).
    window.telsSiteTemplate.mount = String(entry.mount).replace(/\/$/, '') || PUBLIC_MFE_MOUNT;
    window.telsSiteTemplate.origin = entry.origin || '';
  }
  return entry;
}

/** The marketing MFE mount of the site template in use, once a component asked for it; the default mount before. */
function marketingMount() {
  const known = typeof window !== 'undefined' && window.telsSiteTemplate && window.telsSiteTemplate.mount;
  return known || PUBLIC_MFE_MOUNT;
}

/** Resolve the public MFE mount segment (e.g. /public): the selected site template's marketing MFE first. */
function getPublicMfeMount(config) {
  const marketing = getSiteTemplateMarketing(config);
  if (marketing) {
    return String(marketing.mount).replace(/\/$/, '') || PUBLIC_MFE_MOUNT;
  }
  const home = config.INDIGO_HOME_URL;
  if (!isSiteRoot(home)) {
    return String(home).replace(/\/$/, '') || PUBLIC_MFE_MOUNT;
  }

  const courses = config.INDIGO_COURSES_URL;
  if (typeof courses === 'string' && courses.includes('/courses')) {
    const base = courses.replace(/\/courses\/?$/, '');
    if (base && !isSiteRoot(base)) {
      return base;
    }
  }

  return PUBLIC_MFE_MOUNT;
}

/** Ensure a relative path lives under the public MFE mount. */
function ensurePublicMfePath(path, mount = PUBLIC_MFE_MOUNT) {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }

  const m = (mount || PUBLIC_MFE_MOUNT).replace(/\/$/, '') || PUBLIC_MFE_MOUNT;
  const p = path.startsWith('/') ? path : `/${path}`;

  if (p === m || p === `${m}/`) {
    return `${m}/`;
  }
  if (p.startsWith(`${m}/`)) {
    return p;
  }
  if (p === '/') {
    return `${m}/`;
  }
  return `${m}${p}`;
}

/**
 * Resolve marketing paths to the public MFE (e.g. /courses → /public/courses).
 * Uses INDIGO_*_URL when set; always normalizes away bare site-root paths.
 */
function resolvePublicMfeUrl(url, config) {
  const mount = getPublicMfeMount(config);
  // Another origin serves the marketing MFE (tutor dev: one port per MFE): absolute links from other apps.
  const marketing = getSiteTemplateMarketing(config);
  const origin = marketing && marketing.origin
    && (typeof window === 'undefined' || window.location.origin !== marketing.origin) ? marketing.origin : '';
  const onMarketingOrigin = (path) => (path.startsWith('http://') || path.startsWith('https://') ? path : `${origin}${path}`);

  if (!url) {
    return onMarketingOrigin(`${mount}/`);
  }

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  const normalized = url === '/' ? '/' : url.replace(/\/$/, '') || '/';
  if (marketing) {
    // The INDIGO_*_URL settings describe the default marketing MFE; with a site template the route itself
    // (home, /courses, …) is put under that template's mount.
    const route = normalized.startsWith('/') ? toPublicAppPath(normalized) : `/${normalized}`;
    return onMarketingOrigin(ensurePublicMfePath(route, mount));
  }
  const configKey = ROUTE_CONFIG_KEYS[normalized];
  if (configKey && config[configKey]) {
    const configured = String(config[configKey]);
    if (!isSiteRoot(configured)) {
      return onMarketingOrigin(ensurePublicMfePath(configured, mount));
    }
  }

  if (url.startsWith('/')) {
    return onMarketingOrigin(ensurePublicMfePath(url, mount));
  }

  return `${config.LMS_BASE_URL || ''}${url}`;
}

/** Router pathname (basename-relative) for active nav styling inside the public MFE. */
function isPublicMfeNavActive(urlKey, pathname) {
  const path = pathname.replace(/\/$/, '') || '/';

  if (urlKey === 'home') {
    return path === '/';
  }

  const routePath = PUBLIC_ROUTE_BY_KEY[urlKey];
  if (!routePath || routePath === '/') {
    return false;
  }

  const normalized = routePath.replace(/\/$/, '');
  return path === normalized || path.startsWith(`${normalized}/`);
}

/**
 * True inside a marketing MFE: the app's own mount (PUBLIC_PATH) is one of the site templates'
 * marketing mounts (INDIGO_SITE_TEMPLATES) or the configured public mount. Other MFEs link out.
 */
function isMarketingMfe(config) {
  const ownMount = String(process.env.PUBLIC_PATH || '').replace(/\/$/, '');
  if (ownMount === '') {
    return false;
  }
  const templates = (config && config.INDIGO_SITE_TEMPLATES) || {};
  const mounts = Object.values(templates).map((t) => String(t.mount || '').replace(/\/$/, ''));
  return mounts.includes(ownMount) || ownMount === getPublicMfeMount(config);
}

// --- Helpers of the template-2 chrome (native-plus-template-b): absolute public-MFE URLs,
// in-app route paths for react-router links, footer and catalog-search hrefs. ---

function isAbsoluteUrl(value) {
  return typeof value === 'string'
    && (value.startsWith('http://') || value.startsWith('https://'));
}

function stripTrailingSlash(value) {
  const text = String(value || '');
  if (text === '/') {
    return '/';
  }
  return text.replace(/\/$/, '');
}

function splitHref(url) {
  if (!url) {
    return { path: '/', search: '', hash: '' };
  }
  const hashIdx = url.indexOf('#');
  const withoutHash = hashIdx === -1 ? url : url.slice(0, hashIdx);
  const hash = hashIdx === -1 ? '' : url.slice(hashIdx);
  const qIdx = withoutHash.indexOf('?');
  const path = qIdx === -1 ? withoutHash : withoutHash.slice(0, qIdx);
  const search = qIdx === -1 ? '' : withoutHash.slice(qIdx);
  return { path: path || '/', search, hash };
}

/** Collapse /public/public → /public and /public/public/about → /public/about. */
function collapseDoubledMount(pathname) {
  let p = pathname || '/';
  const mount = marketingMount();
  const doubled = `${mount}${mount}`;
  while (p === doubled || p.startsWith(`${doubled}/`)) {
    p = `${mount}${p.slice(doubled.length)}` || mount;
  }
  return p || '/';
}

/**
 * Basename-relative route. Strips every /public prefix because the router
 * basename / home origin already includes it.
 */
function toPublicAppPath(href) {
  if (!href) {
    return '/';
  }
  if (isAbsoluteUrl(href)) {
    try {
      const parsed = new URL(href);
      return toPublicAppPath(`${parsed.pathname}${parsed.search}${parsed.hash}`);
    } catch (err) {
      return href;
    }
  }
  const { path, search, hash } = splitHref(href);
  let appPath = collapseDoubledMount(path.replace(/\/$/, '') || '/');
  // Strip the marketing mount of the template in use and the default one (/public), whichever the href carries.
  const mounts = [...new Set([marketingMount(), PUBLIC_MFE_MOUNT])];
  let stripped = true;
  while (stripped) {
    stripped = false;
    mounts.forEach((mount) => {
      if (appPath === mount || appPath.startsWith(`${mount}/`)) {
        appPath = appPath === mount ? '/' : (appPath.slice(mount.length) || '/');
        stripped = true;
      }
    });
  }
  if (!appPath.startsWith('/')) {
    appPath = `/${appPath}`;
  }
  return `${appPath}${search}${hash}`;
}

/**
 * Public MFE origin. INDIGO_HOME_URL is already
 * http://apps.local.openedx.io:2024/public — do not append /public again.
 */
function getPublicOrigin(config) {
  const marketing = getSiteTemplateMarketing(config);
  if (marketing) {
    return stripTrailingSlash(`${marketing.origin || ''}${marketingMount()}`);
  }
  const home = config && config.INDIGO_HOME_URL;
  if (isAbsoluteUrl(home)) {
    try {
      const parsed = new URL(home);
      const path = collapseDoubledMount(parsed.pathname.replace(/\/$/, '') || PUBLIC_MFE_MOUNT);
      const mount = path === '/' ? PUBLIC_MFE_MOUNT : path;
      return stripTrailingSlash(`${parsed.origin}${mount.startsWith('/') ? mount : `/${mount}`}`);
    } catch (err) {
      return stripTrailingSlash(home);
    }
  }
  if (home && !isSiteRoot(home)) {
    return collapseDoubledMount(stripTrailingSlash(home));
  }
  return PUBLIC_MFE_MOUNT;
}

function withHomeTrailingSlash(origin) {
  const base = stripTrailingSlash(origin);
  return `${base}/`;
}

function joinOnPublicOrigin(origin, appPath) {
  const route = toPublicAppPath(appPath || '/');
  const { path } = splitHref(route);
  const base = stripTrailingSlash(origin);
  if (path === '/') {
    return `${base}/`;
  }
  if (base.endsWith(path)) {
    return base;
  }
  return `${base}${path}`;
}

function collapseAbsolutePublicUrl(url) {
  try {
    const parsed = new URL(url);
    const pathname = collapseDoubledMount(parsed.pathname.replace(/\/$/, '') || '/');
    const isHome = pathname === marketingMount() || pathname === '/';
    if (isHome) {
      return `${parsed.origin}${marketingMount()}/`;
    }
    return `${parsed.origin}${pathname}${parsed.search}${parsed.hash}`;
  } catch (err) {
    return stripTrailingSlash(url);
  }
}

function publicHomeHref(config) {
  return withHomeTrailingSlash(getPublicOrigin(config));
}

/** Footer item → origin + app route. titleKey is an app path, not /public/…. */
function resolveFooterHref(link, config) {
  const fromKey = link && link.titleKey && PUBLIC_ROUTE_BY_KEY[link.titleKey];
  const raw = fromKey || (link && link.url) || '/';
  return resolvePublicMfeUrl(raw, config);
}

function publicCoursesHref(config, query) {
  const params = new URLSearchParams();
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value != null && value !== '') {
      params.set(key, value);
    }
  });
  const qs = params.toString();
  const base = resolvePublicMfeUrl('/courses', config);
  return qs ? `${base}?${qs}` : base;
}
