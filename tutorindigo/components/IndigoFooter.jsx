const DEFAULT_LINKS = [
  { titleKey: 'home', url: '/' },
  { titleKey: 'privacy', url: '/privacy' },
  { titleKey: 'terms', url: '/terms' },
  { titleKey: 'about', url: '/about' },
  { titleKey: 'contact', url: '/contact' },
];

const HIDDEN_FOOTER_KEYS = new Set(['accessibility', 'eea']);
const HIDDEN_FOOTER_PATHS = ['/accessibility', '/eea-privacy-disclosures'];

const isHiddenFooterLink = (link) => {
  if (HIDDEN_FOOTER_KEYS.has(link.titleKey)) {
    return true;
  }
  const url = String(link.url || '');
  return HIDDEN_FOOTER_PATHS.some((path) => url === path || url.endsWith(path));
};

/**
 * Shared marketing footer for all MFEs (PLUGIN_SLOTS → indigo_footer).
 * Template B (Harvard-PLL / tels-mirror). Structure: a single CTA button,
 * the "Footer Links" column (screen-reader-only heading, matching Drupal's
 * own pll.harvard.edu markup), and the site logo — no social icons, no
 * contact block, no bottom copyright bar. The link *set* itself matches
 * tels-mirror's own Footer.tsx (Privacy / Terms / About Us / Contact), not
 * the real Harvard site's (which links Accessibility / EEA Privacy
 * Disclosures instead — not this product's pages). Styles:
 * tels-brand-openedx .tels-footer* (design tokens only).
 */
const indigoFooterMessages = defineMessages({
  exploreCoursesCta: {
    id: 'indigo.footer.exploreCoursesCta',
    defaultMessage: 'Explore courses',
    description: 'Footer CTA button',
  },
  linksHeading: {
    id: 'indigo.footer.links.heading',
    defaultMessage: 'Footer Links',
    description: 'Screen-reader-only heading for the footer legal-links column (matches the live pll.harvard.edu markup, which hides this heading visually)',
  },
  home: { id: 'indigo.footer.link.home', defaultMessage: 'Home', description: 'Footer Home link (public MFE)' },
  privacy: { id: 'indigo.footer.link.privacy', defaultMessage: 'Privacy Policy', description: 'Footer Privacy Policy link' },
  terms: { id: 'indigo.footer.link.terms', defaultMessage: 'Terms of Use', description: 'Footer Terms of Use link' },
  about: { id: 'indigo.footer.link.about', defaultMessage: 'About Us', description: 'Footer About Us link' },
  contact: { id: 'indigo.footer.link.contact', defaultMessage: 'Contact', description: 'Footer Contact link' },
});

const IndigoFooter = () => {
  const intl = useIntl();
  const config = getConfig();
  const siteName = config.SITE_NAME || 'TitanEd';

  const logoUrl = config.LOGO_URL || config.LOGO_WHITE_URL || `${config.LMS_BASE_URL}/theming/asset/images/logo.png`;

  const links = (config.INDIGO_FOOTER_EXPLORE_LINKS || DEFAULT_LINKS)
    .filter((link) => !isHiddenFooterLink(link));

  const homeUrl = publicHomeHref(config);
  const coursesUrl = resolvePublicMfeUrl('/courses', config);

  const linkLabel = (link) => {
    if (link.titleKey && indigoFooterMessages[link.titleKey]) {
      return intl.formatMessage(indigoFooterMessages[link.titleKey]);
    }
    return link.title || link.titleKey || '';
  };

  return (
    <footer className="tels-footer" role="contentinfo">
      <div className="tels-container tels-footer__top">
        <div>
          <a href={coursesUrl} className="tels-btn tels-btn--primary">
            {intl.formatMessage(indigoFooterMessages.exploreCoursesCta)}
          </a>
        </div>

        <div className="tels-footer__col">
          <h2 className="sr-only">{intl.formatMessage(indigoFooterMessages.linksHeading)}</h2>
          <ul>
            {links.map((link) => (
              <li key={`${link.url}-${link.titleKey || link.title}`}>
                <a href={resolveFooterHref(link, config)}>{linkLabel(link)}</a>
              </li>
            ))}
          </ul>
        </div>

        <div className="tels-footer__brand">
          <div className="tels-footer__logo">
            <a href={homeUrl} aria-label={siteName}>
              <img src={logoUrl} alt={siteName} />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};
