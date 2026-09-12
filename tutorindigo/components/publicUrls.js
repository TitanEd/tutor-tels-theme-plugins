/** Public MFE mount. The home/base URL already ends with this (…/public). */
const PUBLIC_MFE_MOUNT = '/public';

const ROUTE_CONFIG_KEYS = {
  '/': 'INDIGO_HOME_URL',
  '/home': 'INDIGO_HOME_URL',
  '/courses': 'INDIGO_COURSES_URL',
  '/about': 'INDIGO_ABOUT_URL',
  '/contact': 'INDIGO_CONTACT_URL',
  '/accessibility': 'INDIGO_ACCESSIBILITY_URL',
  '/privacy': 'INDIGO_PRIVACY_URL',
  '/terms': 'INDIGO_TERMS_URL',
  '/eea-privacy-disclosures': 'INDIGO_EEA_URL',
};

/** App routes only — no /public prefix. Origin already has it. */
const PUBLIC_ROUTE_BY_KEY = {
  home: '/',
  courses: '/courses',
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
  const doubled = `${PUBLIC_MFE_MOUNT}${PUBLIC_MFE_MOUNT}`;
  while (p === doubled || p.startsWith(`${doubled}/`)) {
    p = `${PUBLIC_MFE_MOUNT}${p.slice(doubled.length)}` || PUBLIC_MFE_MOUNT;
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
  while (appPath === PUBLIC_MFE_MOUNT || appPath.startsWith(`${PUBLIC_MFE_MOUNT}/`)) {
    appPath = appPath === PUBLIC_MFE_MOUNT
      ? '/'
      : (appPath.slice(PUBLIC_MFE_MOUNT.length) || '/');
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
    const isHome = pathname === PUBLIC_MFE_MOUNT || pathname === '/';
    if (isHome) {
      return `${parsed.origin}${PUBLIC_MFE_MOUNT}/`;
    }
    return `${parsed.origin}${pathname}${parsed.search}${parsed.hash}`;
  } catch (err) {
    return stripTrailingSlash(url);
  }
}

/**
 * Real browser URL. Home is the origin as-is (already …/public).
 * Other pages are origin + /courses, /about, … — never origin + /public/….
 */
function resolvePublicMfeUrl(url, config) {
  if (isAbsoluteUrl(url)) {
    return collapseAbsolutePublicUrl(url);
  }

  const { search, hash } = splitHref(url || '/');
  const appPath = toPublicAppPath(url || '/');
  const { path } = splitHref(appPath);
  const origin = getPublicOrigin(config);

  if (path === '/') {
    return `${withHomeTrailingSlash(origin)}${search}${hash}`;
  }

  const configKey = ROUTE_CONFIG_KEYS[path];
  if (configKey && config && config[configKey]) {
    const configured = String(config[configKey]);
    if (isAbsoluteUrl(configured)) {
      return `${collapseAbsolutePublicUrl(configured)}${search}${hash}`;
    }
    if (!isSiteRoot(configured)) {
      return `${joinOnPublicOrigin(origin, toPublicAppPath(configured))}${search}${hash}`;
    }
  }

  return `${joinOnPublicOrigin(origin, path)}${search}${hash}`;
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

function getPublicMfeMount(config) {
  const origin = getPublicOrigin(config);
  if (isAbsoluteUrl(origin)) {
    try {
      return new URL(origin).pathname.replace(/\/$/, '') || PUBLIC_MFE_MOUNT;
    } catch (err) {
      return PUBLIC_MFE_MOUNT;
    }
  }
  return origin || PUBLIC_MFE_MOUNT;
}

function ensurePublicMfePath(path, mount = PUBLIC_MFE_MOUNT) {
  if (isAbsoluteUrl(path)) {
    return collapseAbsolutePublicUrl(path);
  }
  const origin = collapseDoubledMount((mount || PUBLIC_MFE_MOUNT).replace(/\/$/, '') || PUBLIC_MFE_MOUNT);
  return joinOnPublicOrigin(origin, toPublicAppPath(path));
}
