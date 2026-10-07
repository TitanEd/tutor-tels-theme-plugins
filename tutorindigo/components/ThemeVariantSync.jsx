// Dark mode for every MFE, including the MFEs that another MFE embeds in an iframe (the discussions
// sidebar of the Learning MFE loads the Discussions MFE, which renders neither header nor footer
// there). Runs once per page load, at module evaluation, before the app initialises.
//
// 1. Start in the variant chosen with the header toggle. ToggleThemeButton stores the choice in the
//    `selected-paragon-theme-variant` cookie, shared by every host of the site, while
//    frontend-platform reads only localStorage, which is per origin and never written in an
//    embedded MFE. Copy the cookie into localStorage so the variant applies without a reload.
// 2. In dark mode, give same-origin iframes that carry no theme of their own (the TinyMCE editor of
//    the Discussions MFE, embedded content) the page background, text and link colors of the dark
//    theme, read from the design tokens of this page. Iframes are styled when they appear and again
//    when their document loads; the style is added once per document.
const telsThemeVariantKey = 'selected-paragon-theme-variant';

const telsStoredThemeVariant = () => {
  try {
    const match = document.cookie.match(new RegExp(`(?:^|; )${telsThemeVariantKey}=(light|dark)`));
    if (match && window.localStorage.getItem(telsThemeVariantKey) !== match[1]) {
      window.localStorage.setItem(telsThemeVariantKey, match[1]);
      window.localStorage.setItem('selected-theme-variant', match[1]);
    }
    return window.localStorage.getItem(telsThemeVariantKey);
  } catch (e) {
    return null; // no cookie or storage access (privacy mode): the MFE keeps its own preference
  }
};

// The dark iframe stylesheet from the tokens of this page, or null while the theme CSS is not loaded yet.
const telsDarkIframeStyle = () => {
  const root = getComputedStyle(document.documentElement);
  const token = (name) => root.getPropertyValue(name).trim();
  const bg = token('--pgn-color-bg-base');
  const text = token('--pgn-color-text-base');
  if (!bg || !text) {
    return null;
  }
  const link = token('--pgn-color-link-base') || text;
  const linkHover = token('--pgn-color-link-hover') || link;
  return `
    body { background-color: ${bg}; color: ${text}; }
    a { color: ${link}; }
    a:hover { color: ${linkHover}; }
  `;
};

const telsStyleDarkIframe = (iframe) => {
  let doc = null;
  try {
    doc = iframe.contentDocument;
  } catch (e) {
    return; // cross-origin iframe: it loads its own theme (see 1.)
  }
  // No document (cross-origin), no <head> yet (document still being created), or already styled.
  if (!doc || !doc.head || doc.head.querySelector('style[data-tels-dark-theme]')) {
    return;
  }
  const css = telsDarkIframeStyle();
  if (!css) {
    return; // tried again on the next change
  }
  const style = doc.createElement('style');
  style.setAttribute('data-tels-dark-theme', '');
  style.textContent = css;
  doc.head.appendChild(style);
};

const telsStyleDarkIframes = () => {
  Array.from(document.getElementsByTagName('iframe')).forEach((iframe) => {
    if (!iframe.dataset.telsDarkListener) {
      iframe.dataset.telsDarkListener = 'true';
      iframe.addEventListener('load', () => telsStyleDarkIframe(iframe));
    }
    telsStyleDarkIframe(iframe);
  });
};

if (telsStoredThemeVariant() === 'dark' && typeof MutationObserver !== 'undefined') {
  const telsDarkIframeObserver = new MutationObserver((mutations) => {
    if (mutations.some((m) => Array.from(m.addedNodes).some((n) => n.nodeType === 1))) {
      telsStyleDarkIframes();
    }
  });
  const telsStartDarkIframes = () => {
    telsStyleDarkIframes();
    telsDarkIframeObserver.observe(document.body, { childList: true, subtree: true });
  };
  if (document.body) {
    telsStartDarkIframes();
  } else {
    document.addEventListener('DOMContentLoaded', telsStartDarkIframes, { once: true });
  }
}
