/**
 * Shared marketing footer for all MFEs (PLUGIN_SLOTS → indigo_footer).
 * Same behavior as mfes/frontend-app-public/src/tels-chrome/IndigoFooter.jsx.
 * Styles: tels-brand-openedx .tels-footer* (design tokens only).
 * Copy: defineMessages + useIntl (same ids as public MFE footer-messages.js).
 */

const SOCIAL_ICONS = {
  linkedin: faLinkedinIn,
  facebook: faFacebookF,
  twitter: faTwitter,
  youtube: faYoutube,
  instagram: faInstagram,
};

const DEFAULT_EXPLORE_LINKS = [
  { titleKey: 'home', url: '/' },
  { titleKey: 'courses', url: '/courses' },
  { titleKey: 'about', url: '/about' },
  { titleKey: 'contact', url: '/contact' },
];

const DEFAULT_COMPANY_LINKS = [
  { titleKey: 'about', url: '/about' },
  { titleKey: 'contact', url: '/contact' },
];

const DEFAULT_SUPPORT_LINKS = [
  { titleKey: 'privacy', url: '/privacy' },
  { titleKey: 'terms', url: '/terms' },
];

const indigoFooterMessages = defineMessages({
  logoAlt: {
    id: 'indigo.footer.logo.altText',
    defaultMessage: '{siteName}',
    description: 'Alt text for the site footer logo',
  },
  socialLabel: {
    id: 'indigo.footer.social.label',
    defaultMessage: 'Social',
    description: 'Aria label for footer social links',
  },
  exploreHeading: {
    id: 'indigo.footer.explore.heading',
    defaultMessage: 'Explore',
    description: 'Footer Explore column heading',
  },
  companyHeading: {
    id: 'indigo.footer.company.heading',
    defaultMessage: 'Company',
    description: 'Footer Company column heading',
  },
  supportHeading: {
    id: 'indigo.footer.support.heading',
    defaultMessage: 'Support',
    description: 'Footer Support column heading',
  },
  contactHeading: {
    id: 'indigo.footer.contact.heading',
    defaultMessage: 'Contact',
    description: 'Footer Contact column heading',
  },
  home: {
    id: 'indigo.footer.link.home',
    defaultMessage: 'Home',
    description: 'Footer Home link',
  },
  courses: {
    id: 'indigo.footer.link.courses',
    defaultMessage: 'Courses',
    description: 'Footer Courses link',
  },
  about: {
    id: 'indigo.footer.link.about',
    defaultMessage: 'About Us',
    description: 'Footer About Us link',
  },
  contact: {
    id: 'indigo.footer.link.contact',
    defaultMessage: 'Contact',
    description: 'Footer Contact link',
  },
  privacy: {
    id: 'indigo.footer.link.privacy',
    defaultMessage: 'Privacy Policy',
    description: 'Footer Privacy Policy link',
  },
  terms: {
    id: 'indigo.footer.link.terms',
    defaultMessage: 'Terms & Conditions',
    description: 'Footer Terms & Conditions link',
  },
  emailLabel: {
    id: 'indigo.footer.contact.emailLabel',
    defaultMessage: 'Email:',
    description: 'Label before footer contact email',
  },
  webLabel: {
    id: 'indigo.footer.contact.webLabel',
    defaultMessage: 'Web:',
    description: 'Label before footer website',
  },
  supportNotePrefix: {
    id: 'indigo.footer.contact.supportNotePrefix',
    defaultMessage: 'Request support via ',
    description: 'Text before the contact form link in the footer',
  },
  contactForm: {
    id: 'indigo.footer.contact.formLink',
    defaultMessage: 'Contact form',
    description: 'Contact form link text in footer support note',
  },
  supportNoteSuffix: {
    id: 'indigo.footer.contact.supportNoteSuffix',
    defaultMessage: '.',
    description: 'Punctuation after the contact form link in the footer',
  },
  copyright: {
    id: 'indigo.footer.copyright',
    defaultMessage: '© {year} {siteName}. All rights reserved.',
    description: 'Footer copyright line',
  },
  poweredBy: {
    id: 'indigo.footer.poweredBy',
    defaultMessage: 'Powered by Open edX® · TELS by TitanEd',
    description: 'Footer powered-by line',
  },
});

const IndigoFooter = () => {
  const intl = useIntl();
  const config = getConfig();
  const siteName = config.SITE_NAME || 'TitanEd';
  const year = new Date().getFullYear();
  const logoUrl = config.LOGO_URL
    || config.LOGO_WHITE_URL
    || `${config.LMS_BASE_URL}/theming/asset/images/logo.png`;
  const socialLinks = config.INDIGO_FOOTER_SOCIAL_LINKS || [];
  const exploreLinks = config.INDIGO_FOOTER_EXPLORE_LINKS || DEFAULT_EXPLORE_LINKS;
  const companyLinks = config.INDIGO_FOOTER_COMPANY_LINKS || DEFAULT_COMPANY_LINKS;
  const supportLinks = config.INDIGO_FOOTER_SUPPORT_LINKS || DEFAULT_SUPPORT_LINKS;
  const contact = config.INDIGO_FOOTER_CONTACT || {};
  const contactEmail = contact.email || 'Legal@TitanEd.com';
  const contactWebUrl = contact.web_url || 'https://titaned.com/';
  const contactWebLabel = contact.web_label || 'titaned.com';
  const addressLines = contact.address_lines || ['TitanEd, Gurugram,', 'Haryana, India'];

  // Home/Courses/About/Contact/Privacy/Terms → public MFE (see publicUrls.js).
  const resolveUrl = (url) => resolvePublicMfeUrl(url, config);

  const linkTitle = (link) => {
    if (link.titleKey && link.titleKey in indigoFooterMessages) {
      return intl.formatMessage(indigoFooterMessages[link.titleKey]);
    }
    return link.title || link.titleKey || '';
  };

  const renderLinkColumn = (headingMessage, links) => (
    <div className="tels-footer__col">
      <h4>{intl.formatMessage(headingMessage)}</h4>
      <ul>
        {links.map((link) => (
          <li key={`${link.url}-${link.titleKey || link.title}`}>
            <a href={resolveUrl(link.url)}>{linkTitle(link)}</a>
          </li>
        ))}
      </ul>
    </div>
  );

  const contactFormHref = resolveUrl(
    (exploreLinks.find((l) => l.titleKey === 'contact') || {}).url || '/contact',
  );

  return (
    <footer className="tels-footer" role="contentinfo">
      <div className="tels-container">
        <div className="tels-footer__top">
          <div className="tels-footer__logo">
            <a href={resolveUrl('/')}>
              <img
                src={logoUrl}
                alt={intl.formatMessage(indigoFooterMessages.logoAlt, { siteName })}
              />
            </a>
          </div>
          {socialLinks.length > 0 && (
            <div
              className="tels-footer__social"
              aria-label={intl.formatMessage(indigoFooterMessages.socialLabel)}
            >
              {socialLinks.map((item) => {
                const icon = SOCIAL_ICONS[item.name];
                if (!icon) {
                  return null;
                }
                return (
                  <a
                    key={item.name}
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={item.label || item.name}
                  >
                    <FontAwesomeIcon icon={icon} />
                  </a>
                );
              })}
            </div>
          )}
        </div>

        <div className="tels-footer__cols">
          {renderLinkColumn(indigoFooterMessages.exploreHeading, exploreLinks)}
          {renderLinkColumn(indigoFooterMessages.companyHeading, companyLinks)}
          {renderLinkColumn(indigoFooterMessages.supportHeading, supportLinks)}
          <div className="tels-footer__col tels-footer__contact">
            <h4>{intl.formatMessage(indigoFooterMessages.contactHeading)}</h4>
            <p>
              {intl.formatMessage(indigoFooterMessages.emailLabel)}
              {' '}
              <a href={`mailto:${contactEmail}`}>{contactEmail}</a>
            </p>
            <p>
              {intl.formatMessage(indigoFooterMessages.webLabel)}
              {' '}
              <a href={contactWebUrl} target="_blank" rel="noreferrer">
                {contactWebLabel}
              </a>
            </p>
            <p>
              {addressLines.map((line, index) => (
                <React.Fragment key={line}>
                  {line}
                  {index < addressLines.length - 1 && <br />}
                </React.Fragment>
              ))}
            </p>
            <p className="tels-footer__contact-note">
              {intl.formatMessage(indigoFooterMessages.supportNotePrefix)}
              <a href={contactFormHref}>
                {intl.formatMessage(indigoFooterMessages.contactForm)}
              </a>
              {intl.formatMessage(indigoFooterMessages.supportNoteSuffix)}
            </p>
          </div>
        </div>

        <div className="tels-footer__bottom">
          <span>
            {intl.formatMessage(indigoFooterMessages.copyright, { year, siteName })}
          </span>
          <span>{intl.formatMessage(indigoFooterMessages.poweredBy)}</span>
        </div>
      </div>
    </footer>
  );
};
