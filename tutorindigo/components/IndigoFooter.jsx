
// Site footer of every MFE (except authoring, which has the Studio footer): three columns -- logo and social
// links | footer links (INDIGO_FOOTER_NAV_LINKS) | address and contact email -- and the copyright below.
// Address, email, social links and copyright come from control-panel's theme configuration page
// (FOOTER_CONFIG_URL = LMS_ROOT_URL/ui_configuration/footer-config); the logo from LOGO_URL / LOGO_WHITE_URL
// (dark mode). Colors and fonts are the design tokens, so the footer follows the theme in light and dark mode.
let telsFooterConfigRequest = null;
const loadTelsFooterConfig = (url) => {
  if (!telsFooterConfigRequest) {
    telsFooterConfigRequest = fetch(url, { credentials: "omit" })
      .then((response) => (response.ok ? response.json() : {}))
      .catch(() => ({}));
  }
  return telsFooterConfigRequest;
};

const TELS_SOCIAL_ICONS = {
  facebook: (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M24 12.07C24 5.41 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.04V9.41c0-3.02 1.8-4.7 4.54-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.5c-1.5 0-1.96.93-1.96 1.89v2.26h3.32l-.53 3.5h-2.8V24C19.62 23.1 24 18.1 24 12.07z" /></svg>
  ),
  instagram: (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5" /><circle cx="12" cy="12" r="4.5" /><circle cx="17.6" cy="6.4" r="1.2" fill="currentColor" stroke="none" /></svg>
  ),
  twitter: (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>
  ),
  linkedin: (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z" /></svg>
  ),
  youtube: (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31.3 31.3 0 0 0 0 12a31.3 31.3 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31.3 31.3 0 0 0 24 12a31.3 31.3 0 0 0-.5-5.8zM9.6 15.6V8.4l6.3 3.6-6.3 3.6z" /></svg>
  ),
};
const TELS_SOCIAL_NAMES = {
  facebook: "Facebook", instagram: "Instagram", twitter: "X", linkedin: "LinkedIn", youtube: "YouTube",
};

const TELS_FOOTER_STYLE = `
  .tels-footer {
    margin-top: 3rem;
    border-top: 1px solid var(--pgn-color-light-400);
    color: var(--pgn-color-text-footer, var(--pgn-color-body-base));
    font-family: var(--pgn-typography-font-family-base);
  }
  .tels-footer__inner {
    max-width: var(--pgn-size-container-max-width-xl, 1440px);
    margin: 0 auto;
    padding: 3rem calc(var(--pgn-spacing-grid-gutter-width, 1.5rem) * .5) 0;
    box-sizing: border-box;
  }
  .tels-footer__grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr);
    gap: 2rem 3rem;
    align-items: start;
  }
  .tels-footer__brand { display: flex; flex-direction: column; align-items: flex-start; gap: 1.25rem; }
  .tels-footer__logo { display: inline-flex; }
  .tels-footer__logo img { max-height: 48px; max-width: 220px; object-fit: contain; }
  .tels-footer__logo .tels-footer__logo-dark { display: none; }
  [data-paragon-theme-variant="dark"] .tels-footer__logo .tels-footer__logo-light { display: none; }
  [data-paragon-theme-variant="dark"] .tels-footer__logo .tels-footer__logo-dark { display: block; }
  .tels-footer__social { display: flex; flex-wrap: wrap; gap: .5rem; margin: 0; padding: 0; list-style: none; }
  .tels-footer__social a {
    display: inline-flex; align-items: center; justify-content: center; width: 2.25rem; height: 2.25rem;
    border: 1px solid var(--pgn-color-light-400); border-radius: 50%;
    background: var(--pgn-color-bg-base, #fff); color: var(--pgn-color-body-base) !important;
    transition: background-color .15s ease, color .15s ease, border-color .15s ease;
  }
  .tels-footer__social a:hover, .tels-footer__social a:focus-visible {
    background: var(--pgn-color-primary-base); border-color: var(--pgn-color-primary-base); color: #fff !important;
  }
  .tels-footer__social svg { width: 1.5rem; height: 1.5rem; }
  .tels-footer__links { justify-self: center; text-align: center; }
  .tels-footer__links ul { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: .625rem; }
  .tels-footer__links ul li {display: inline-block;}
  .tels-footer__links a { color: var(--pgn-color-body-base) !important; text-decoration: none !important; font-weight: 500; }
  .tels-footer__links a:hover, .tels-footer__links a:focus-visible { color: var(--pgn-color-primary-base) !important; text-decoration: underline !important; }
  .tels-footer__contact { justify-self: end; display: flex; flex-direction: column; align-items: flex-end; gap: .75rem; text-align: end; }
  .tels-footer__contact address { margin: 0; font-style: normal; line-height: 1.6; }
  .tels-footer__contact-row { display: inline-flex; align-items: flex-start; gap: .5rem; }
  .tels-footer__contact-row svg { flex: none; width: 1.125rem; height: 1.125rem; margin-top: .2rem; color: var(--pgn-color-primary-base); }
  .tels-footer__contact a { color: var(--pgn-color-body-base) !important; overflow-wrap: anywhere; }
  .tels-footer__contact a:hover { color: var(--pgn-color-primary-base) !important; }
  .tels-footer__bottom {
    margin-top: 2.5rem; padding: 1.25rem 0; border-top: 1px solid var(--pgn-color-light-400);
    text-align: center; font-size: .875rem;
  }
  @media (max-width: 767.98px) {
    .tels-footer__inner { padding-top: 2.25rem; }
    .tels-footer__grid { grid-template-columns: minmax(0, 1fr); gap: 2rem; }
    .tels-footer__brand, .tels-footer__contact { align-items: center; justify-self: center; text-align: center; }
    .tels-footer__social { justify-content: center; }
    .tels-footer__contact-row { justify-content: center; }
  }
  @media (prefers-reduced-motion: reduce) { .tels-footer__social a { transition: none; } }
`;

const IndigoFooter = () => {
  const intl = useIntl();
  const config = getConfig();
  const [footer, setFooter] = useState({});

  const indigoFooterNavLinks = config.INDIGO_FOOTER_NAV_LINKS || [];
  const BASE_URL = config.LMS_BASE_URL;
  // Live branding (control-panel ui_configuration) serves the admin-uploaded logos.
  const logoUrl = (config.INDIGO_LIVE_BRANDING && config.LOGO_URL) || `${BASE_URL}/static/indigo/images/logo.png`;
  const logoDarkUrl = (config.INDIGO_LIVE_BRANDING && (config.LOGO_WHITE_URL || config.FOOTER_LOGO_URL)) || `${BASE_URL}/static/indigo/images/logo-white.png`;

  useEffect(() => {
    if (!config.FOOTER_CONFIG_URL) { return undefined; }
    let active = true;
    loadTelsFooterConfig(config.FOOTER_CONFIG_URL).then((data) => { if (active) { setFooter(data || {}); } });
    return () => { active = false; };
  }, [config.FOOTER_CONFIG_URL]);

  const messages = {
    "footer.copyright.text": {
      id: "footer.copyright.text",
      defaultMessage: `Copyrights ©${new Date().getFullYear()}. All Rights Reserved.`,
      description: "copyright text for the footer",
    },
    "footer.links.label": {
      id: "footer.links.label",
      defaultMessage: "Footer",
      description: "accessible name of the footer links",
    },
    "footer.social.label": {
      id: "footer.social.label",
      defaultMessage: "Social media",
      description: "accessible name of the social media links in the footer",
    },
    "footer.home.label": {
      id: "footer.home.label",
      defaultMessage: "Home",
      description: "accessible name of the footer logo link",
    },
  };

  const addressLines = Array.isArray(footer.address_lines) ? footer.address_lines : [];
  const socialLinks = (Array.isArray(footer.social_links) ? footer.social_links : [])
    .filter((link) => link && TELS_SOCIAL_ICONS[link.name] && /^https?:\/\//i.test(link.url || ""));
  const linkUrl = (url) => (url.startsWith("http") ? url : BASE_URL + url);

  return (
    <footer className="tels-footer" role="contentinfo">
      <style>{TELS_FOOTER_STYLE}</style>
      <div className="tels-footer__inner">
        <div className="tels-footer__grid">
          <div className="tels-footer__brand">
            <a className="tels-footer__logo" href={BASE_URL} aria-label={intl.formatMessage(messages["footer.home.label"])}>
              <img className="tels-footer__logo-light" src={logoUrl} alt="" />
              <img className="tels-footer__logo-dark" src={logoDarkUrl} alt="" />
            </a>
            {socialLinks.length > 0 && (
              <ul className="tels-footer__social" aria-label={intl.formatMessage(messages["footer.social.label"])}>
                {socialLinks.map((link) => (
                  <li key={link.name}>
                    <a href={link.url} target="_blank" rel="noopener noreferrer" aria-label={TELS_SOCIAL_NAMES[link.name]} title={TELS_SOCIAL_NAMES[link.name]}>
                      {TELS_SOCIAL_ICONS[link.name]}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <nav className="tels-footer__links" aria-label={intl.formatMessage(messages["footer.links.label"])}>
            <ul>
              {indigoFooterNavLinks.map((link) => (
                <li key={link.url}><a href={linkUrl(link.url)}>{link.title}</a></li>
              ))}
            </ul>
          </nav>
          <div className="tels-footer__contact">
            {addressLines.length > 0 && (
              <div className="tels-footer__contact-row">
                <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" /></svg>
                <address>{addressLines.map((line) => <div key={line}>{line}</div>)}</address>
              </div>
            )}
            {footer.contact_email && (
              <div className="tels-footer__contact-row">
                <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z" /></svg>
                <a href={`mailto:${footer.contact_email}`}>{footer.contact_email}</a>
              </div>
            )}
          </div>
        </div>
        <div className="tels-footer__bottom">
          {footer.copyright_text || intl.formatMessage(messages["footer.copyright.text"])}
        </div>
      </div>
    </footer>
  );
};
