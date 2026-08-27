/** Tutor default public MFE mount (PUBLIC_PATH=/public). */
const PUBLIC_MFE_MOUNT = '/public';

const ROUTE_CONFIG_KEYS = {
  '/': 'INDIGO_HOME_URL',
  '/home': 'INDIGO_HOME_URL',
  '/catalog': 'INDIGO_CATALOG_URL',
  '/courses': 'INDIGO_COURSES_URL',
  '/about': 'INDIGO_ABOUT_URL',
  '/contact': 'INDIGO_CONTACT_URL',
  '/accessibility': 'INDIGO_ACCESSIBILITY_URL',
  '/privacy': 'INDIGO_PRIVACY_URL',
  '/terms': 'INDIGO_TERMS_URL',
  '/eea-privacy-disclosures': 'INDIGO_EEA_URL',
};

/** Marketing route path per header/footer urlKey. */
const PUBLIC_ROUTE_BY_KEY = {
  home: '/',
  catalog: '/catalog',
  courses: '/catalog',
  about: '/about',
  contact: '/contact',
  accessibility: '/accessibility',
  privacy: '/privacy',
  terms: '/terms',
  eea: '/eea-privacy-disclosures',
};

function isSiteRoot(value) {
  return !value || value === '/' || value === '';
}

/** Resolve the public MFE mount segment (e.g. /public). */
function getPublicMfeMount(config) {
  const home = config.INDIGO_HOME_URL;
  if (!isSiteRoot(home)) {
    return String(home).replace(/\/$/, '') || PUBLIC_MFE_MOUNT;
  }

  const catalog = config.INDIGO_CATALOG_URL;
  if (typeof catalog === 'string' && catalog.includes('/catalog')) {
    const base = catalog.replace(/\/catalog\/?$/, '');
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
 * Resolve marketing paths to the public MFE (e.g. /catalog → /public/catalog).
 * Uses INDIGO_*_URL when set; always normalizes away bare site-root paths.
 */
function resolvePublicMfeUrl(url, config) {
  const mount = getPublicMfeMount(config);

  if (!url) {
    return `${mount}/`;
  }

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  const normalized = url === '/' ? '/' : url.replace(/\/$/, '') || '/';
  const configKey = ROUTE_CONFIG_KEYS[normalized];
  if (configKey && config[configKey]) {
    const configured = String(config[configKey]);
    if (!isSiteRoot(configured)) {
      return ensurePublicMfePath(configured, mount);
    }
  }

  if (url.startsWith('/')) {
    return ensurePublicMfePath(url, mount);
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
