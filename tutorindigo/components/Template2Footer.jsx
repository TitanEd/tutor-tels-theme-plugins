// Site template "template-2" footer. Rendered by SiteFooter.jsx when template-2 is selected; styled by
// tels-brand-openedx paragon/templates/template-2/_footer.scss. Left: address and contact email; centre: links;
// right: logo and social links; bottom: copyright.
const TEMPLATE2_DEFAULT_LINKS = [
  { titleKey: 'home', url: '/' },
  { titleKey: 'privacy', url: '/privacy' },
  { titleKey: 'terms', url: '/terms' },
  { titleKey: 'about', url: '/about' },
  { titleKey: 'contact', url: '/contact' },
];

const TEMPLATE2_HIDDEN_FOOTER_KEYS = new Set(['accessibility', 'eea']);
const TEMPLATE2_HIDDEN_FOOTER_PATHS = ['/accessibility', '/eea-privacy-disclosures'];

const template2IsHiddenFooterLink = (link) => {
  if (TEMPLATE2_HIDDEN_FOOTER_KEYS.has(link.titleKey)) {
    return true;
  }
  const url = String(link.url || '');
  return TEMPLATE2_HIDDEN_FOOTER_PATHS.some((path) => url === path || url.endsWith(path));
};

/**
 * Shared marketing footer for all MFEs (PLUGIN_SLOTS → indigo_footer) of template-2.
 * Styles: tels-brand-openedx .tels-footer* (design tokens only).
 */
const template2FooterMessages = defineMessages({
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
  courses: { id: 'indigo.footer.link.courses', defaultMessage: 'Courses', description: 'Footer Courses link' },
  privacy: { id: 'indigo.footer.link.privacy', defaultMessage: 'Privacy Policy', description: 'Footer Privacy Policy link' },
  terms: { id: 'indigo.footer.link.termsOfUse', defaultMessage: 'Terms of Use', description: 'Footer Terms of Use link' },
  about: { id: 'indigo.footer.link.about', defaultMessage: 'About Us', description: 'Footer About Us link' },
  contact: { id: 'indigo.footer.link.contact', defaultMessage: 'Contact', description: 'Footer Contact link' },
  homeAria: {
    id: 'indigo.footer.logo.aria',
    defaultMessage: '{siteName} Home',
    description: 'Footer logo link aria-label',
  },
  logoAlt: {
    id: 'indigo.footer.logo.alt',
    defaultMessage: '{siteName}',
    description: 'Footer logo image alt text',
  },
  contactHeading: {
    id: 'indigo.footer.contact.heading',
    defaultMessage: 'Contact',
    description: 'Footer contact column heading (visually hidden)',
  },
  socialLabel: {
    id: 'indigo.footer.social.mediaLabel',
    defaultMessage: 'Social media',
    description: 'Footer social links list label',
  },
  copyright: {
    id: 'indigo.footer.copyright',
    defaultMessage: '© {year} {siteName}. All rights reserved.',
    description: 'Footer copyright line',
  },
});

// Address, contact email, social links and copyright come from the footer settings of control-panel's
// theme configuration page (FOOTER_CONFIG_URL), the INDIGO_FOOTER_* Tutor settings being the fallback.
let template2FooterConfigRequest = null;
const template2LoadFooterConfig = (url) => {
  if (!template2FooterConfigRequest) {
    template2FooterConfigRequest = fetch(url, { credentials: 'omit' })
      .then((response) => (response.ok ? response.json() : {}))
      .catch(() => ({}));
  }
  return template2FooterConfigRequest;
};

const TEMPLATE2_SOCIAL_ICONS = {
  facebook: faFacebookF,
  instagram: faInstagram,
  twitter: faTwitter,
  linkedin: faLinkedinIn,
  youtube: faYoutube,
};
const TEMPLATE2_SOCIAL_NAMES = {
  facebook: 'Facebook', instagram: 'Instagram', twitter: 'X', linkedin: 'LinkedIn', youtube: 'YouTube',
};
const TEMPLATE2_HIDDEN_LINK_KEYS = new Set(['accessibility', 'eea']);

const Template2Footer = () => {
  const intl = useIntl();
  const config = getConfig();
  const siteName = config.SITE_NAME || 'TitanEd';
  const year = new Date().getFullYear();
  const logoUrl = config.LOGO_URL || config.LOGO_WHITE_URL || `${config.LMS_BASE_URL}/theming/asset/images/logo.png`;

  const [live, setLive] = useState({});
  useEffect(() => {
    if (!config.FOOTER_CONFIG_URL) { return undefined; }
    let cancelled = false;
    template2LoadFooterConfig(config.FOOTER_CONFIG_URL).then((data) => { if (!cancelled) { setLive(data || {}); } });
    return () => { cancelled = true; };
  }, [config.FOOTER_CONFIG_URL]);

  // Centre column: the explore and support links (Home, About, Contact, Privacy Policy, Terms of Use).
  const configured = [...(config.INDIGO_FOOTER_EXPLORE_LINKS || []), ...(config.INDIGO_FOOTER_SUPPORT_LINKS || [])];
  const seen = new Set();
  const links = (configured.length ? configured : TEMPLATE2_DEFAULT_LINKS)
    .filter((link) => !template2IsHiddenFooterLink(link) && !TEMPLATE2_HIDDEN_LINK_KEYS.has(link.titleKey))
    .filter((link) => !seen.has(link.url) && seen.add(link.url));
  const linkLabel = (link) => {
    if (link.titleKey && template2FooterMessages[link.titleKey]) {
      return intl.formatMessage(template2FooterMessages[link.titleKey]);
    }
    return link.title || link.titleKey || '';
  };

  const contact = config.INDIGO_FOOTER_CONTACT || {};
  const addressLines = Array.isArray(live.address_lines) && live.address_lines.length
    ? live.address_lines
    : (contact.address_lines || []);
  const contactEmail = live.contact_email || contact.email || '';
  const socialLinks = (Array.isArray(live.social_links) && live.social_links.length
    ? live.social_links
    : (config.INDIGO_FOOTER_SOCIAL_LINKS || [])
  ).filter((link) => link && TEMPLATE2_SOCIAL_ICONS[link.name] && /^https?:\/\//i.test(link.url || ''));
  // The admin's copyright text is free-form (not translated); the default English line is translated.
  const copyrightOverride = String(live.copyright_text || '').replace('{year}', year).replace('{siteName}', siteName);
  // "© <year> <name>. All rights reserved." (the default wording) is shown translated, with that name.
  const copyrightDefault = copyrightOverride.match(/^©\s*\d{4}\s+(.+?)\.?\s*All rights reserved\.?$/i);
  const copyright = copyrightOverride && !copyrightDefault
    ? copyrightOverride
    : intl.formatMessage(template2FooterMessages.copyright, { year, siteName: copyrightDefault ? copyrightDefault[1] : siteName });

  return (
    <footer className="tels-footer" role="contentinfo">
      <div className="tels-container tels-footer__top">
        <div className="tels-footer__contact">
          <h2 className="sr-only">{intl.formatMessage(template2FooterMessages.contactHeading)}</h2>
          {addressLines.length > 0 && (
            <address>{addressLines.map((line) => <div key={line}>{line}</div>)}</address>
          )}
          {contactEmail && <a href={`mailto:${contactEmail}`}>{contactEmail}</a>}
        </div>

        <div className="tels-footer__col">
          <h2 className="sr-only">{intl.formatMessage(template2FooterMessages.linksHeading)}</h2>
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
            <a href={publicHomeHref(config)} aria-label={intl.formatMessage(template2FooterMessages.homeAria, { siteName })}>
              <img
                src={logoUrl}
                alt={intl.formatMessage(template2FooterMessages.logoAlt, { siteName })}
              />
            </a>
          </div>
          {socialLinks.length > 0 && (
            <ul className="tels-footer__social" aria-label={intl.formatMessage(template2FooterMessages.socialLabel)}>
              {socialLinks.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={link.label || TEMPLATE2_SOCIAL_NAMES[link.name]}
                    title={link.label || TEMPLATE2_SOCIAL_NAMES[link.name]}
                  >
                    <FontAwesomeIcon icon={TEMPLATE2_SOCIAL_ICONS[link.name]} />
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      <div className="tels-container tels-footer__bottom">
        <span>{copyright}</span>
      </div>
    </footer>
  );
};
