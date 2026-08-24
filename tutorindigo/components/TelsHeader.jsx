/**
 * Shared marketing header for MFEs that mount HeaderSlot
 * (PLUGIN_SLOTS → org.openedx.frontend.layout.header.v1).
 *
 * Same behavior as mfes/frontend-app-public/src/tels-chrome/TelsHeader.jsx.
 * Logged out: Home | Courses | About Us | Contact + Sign In / Register
 * Logged in:  Home | Dashboard | Courses | About Us | Contact + user menu
 * Styles: tels-brand-openedx .tels-header* / .tels-btn* (tokens only).
 * Copy: defineMessages + useIntl (same ids as public MFE messages.js).
 */

const DEFAULT_GUEST_NAV = [
  { titleKey: 'home', urlKey: 'home' },
  { titleKey: 'courses', urlKey: 'courses' },
  { titleKey: 'about', urlKey: 'about' },
  { titleKey: 'contact', urlKey: 'contact' },
];

const DEFAULT_AUTH_NAV = [
  { titleKey: 'home', urlKey: 'home' },
  { titleKey: 'dashboard', urlKey: 'dashboard' },
  { titleKey: 'courses', urlKey: 'courses' },
  { titleKey: 'about', urlKey: 'about' },
  { titleKey: 'contact', urlKey: 'contact' },
];

const telsHeaderMessages = defineMessages({
  homeAria: {
    id: 'tels.header.logo.aria',
    defaultMessage: '{siteName} Home',
    description: 'Aria label for the header logo home link',
  },
  primaryNav: {
    id: 'tels.header.nav.aria',
    defaultMessage: 'Primary',
    description: 'Aria label for primary navigation',
  },
  home: {
    id: 'tels.header.nav.home',
    defaultMessage: 'Home',
    description: 'Header Home link',
  },
  dashboard: {
    id: 'tels.header.nav.dashboard',
    defaultMessage: 'Dashboard',
    description: 'Header Dashboard link',
  },
  courses: {
    id: 'tels.header.nav.courses',
    defaultMessage: 'Courses',
    description: 'Header Courses link',
  },
  about: {
    id: 'tels.header.nav.about',
    defaultMessage: 'About Us',
    description: 'Header About Us link',
  },
  contact: {
    id: 'tels.header.nav.contact',
    defaultMessage: 'Contact',
    description: 'Header Contact link',
  },
  signIn: {
    id: 'tels.header.actions.signIn',
    defaultMessage: 'Sign In',
    description: 'Header Sign In button',
  },
  register: {
    id: 'tels.header.actions.register',
    defaultMessage: 'Register',
    description: 'Header Register button',
  },
  menu: {
    id: 'tels.header.mobile.menu',
    defaultMessage: 'Menu',
    description: 'Mobile menu toggle aria label',
  },
  userMenu: {
    id: 'tels.header.user.menu',
    defaultMessage: 'User menu',
    description: 'Authenticated user menu toggle aria label',
  },
  profile: {
    id: 'tels.header.user.profile',
    defaultMessage: 'Profile',
    description: 'User dropdown Profile link',
  },
  account: {
    id: 'tels.header.user.account',
    defaultMessage: 'Account',
    description: 'User dropdown Account settings link',
  },
  logout: {
    id: 'tels.header.user.logout',
    defaultMessage: 'Sign Out',
    description: 'User dropdown Sign Out link',
  },
});

const TelsHeader = () => {
  const intl = useIntl();
  const config = getConfig();
  const { authenticatedUser } = useContext(AppContext);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);

  const siteName = config.SITE_NAME || 'TitanEd';
  const logoUrl = config.LOGO_URL || `${config.LMS_BASE_URL}/theming/asset/images/logo.png`;
  const homeUrl = resolvePublicMfeUrl('/', config);
  const dashboardUrl = config.LEARNER_DASHBOARD_URL
    || config.LEARNER_DASHBOARD_BASE_URL
    || `${config.LMS_BASE_URL}/dashboard`;
  const loginUrl = config.LOGIN_URL;
  const registerUrl = config.REGISTER_URL || `${config.LMS_BASE_URL}/register`;
  const logoutUrl = config.LOGOUT_URL;
  const profileUrl = authenticatedUser && config.ACCOUNT_PROFILE_URL
    ? `${config.ACCOUNT_PROFILE_URL}/u/${authenticatedUser.username}`
    : null;
  const accountUrl = config.ACCOUNT_SETTINGS_URL;
  const isPublicMfe = process.env.APP_ID === 'public';
  const guestNav = config.INDIGO_HEADER_GUEST_NAV || DEFAULT_GUEST_NAV;
  const authNav = config.INDIGO_HEADER_AUTH_NAV || DEFAULT_AUTH_NAV;
  const navItems = authenticatedUser ? authNav : guestNav;
  const location = useLocation();

  useEffect(() => {
    const onDocClick = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  const labelFor = (titleKey) => {
    if (titleKey in telsHeaderMessages) {
      return intl.formatMessage(telsHeaderMessages[titleKey]);
    }
    return titleKey;
  };

  const hrefFor = (item) => {
    if (item.urlKey === 'dashboard') {
      return dashboardUrl;
    }
    if (item.url?.startsWith('http')) {
      return item.url;
    }
    const path = item.url || PUBLIC_ROUTE_BY_KEY[item.urlKey] || '/';
    return resolvePublicMfeUrl(path, config);
  };

  const renderNavItemLink = (item, { onClick, className, key } = {}) => {
    const href = hrefFor(item);
    const label = labelFor(item.titleKey);
    const navClass = ['tels-header__nav-link', className].filter(Boolean).join(' ');
    const active = isPublicMfe
      ? isPublicMfeNavActive(item.urlKey, location.pathname)
      : window.location.pathname.replace(/\/$/, '') === String(href).replace(/\/$/, '');
    return (
      <a
        key={key}
        href={href}
        className={[navClass, active ? 'active' : ''].filter(Boolean).join(' ')}
        onClick={onClick}
        aria-current={active ? 'page' : undefined}
      >
        {label}
      </a>
    );
  };

  const closeMobile = () => setMobileOpen(false);

  return (
    <header className="tels-header">
      <div className="tels-container">
        <div className="tels-header__row">
          <a
            href={homeUrl}
            className="tels-header__logo"
            aria-label={intl.formatMessage(telsHeaderMessages.homeAria, { siteName })}
          >
            <img src={logoUrl} alt={siteName} />
          </a>

          <nav className="tels-header__nav" aria-label={intl.formatMessage(telsHeaderMessages.primaryNav)}>
            {navItems.map((item) => renderNavItemLink(item, {
              key: `${item.titleKey}-${item.urlKey}`,
            }))}
          </nav>

          <div className="tels-header__actions">
            {authenticatedUser ? (
              <div className="tels-header__user" ref={userMenuRef}>
                <button
                  type="button"
                  className="tels-header__user-toggle"
                  aria-label={intl.formatMessage(telsHeaderMessages.userMenu)}
                  aria-expanded={userMenuOpen}
                  onClick={() => setUserMenuOpen((open) => !open)}
                >
                  <span className="tels-header__user-name">
                    {authenticatedUser.name || authenticatedUser.username}
                  </span>
                  <FontAwesomeIcon icon={faChevronDown} aria-hidden="true" />
                </button>
                {userMenuOpen && (
                  <ul className="tels-header__user-menu">
                    {profileUrl && (
                      <li>
                        <a href={profileUrl} onClick={() => setUserMenuOpen(false)}>
                          {intl.formatMessage(telsHeaderMessages.profile)}
                        </a>
                      </li>
                    )}
                    {accountUrl && (
                      <li>
                        <a href={accountUrl} onClick={() => setUserMenuOpen(false)}>
                          {intl.formatMessage(telsHeaderMessages.account)}
                        </a>
                      </li>
                    )}
                    <li>
                      <a href={dashboardUrl} onClick={() => setUserMenuOpen(false)}>
                        {intl.formatMessage(telsHeaderMessages.dashboard)}
                      </a>
                    </li>
                    <li>
                      <a href={logoutUrl}>{intl.formatMessage(telsHeaderMessages.logout)}</a>
                    </li>
                  </ul>
                )}
              </div>
            ) : (
              <>
                <a href={loginUrl} className="tels-btn tels-btn--ghost tels-btn--sm">
                  {intl.formatMessage(telsHeaderMessages.signIn)}
                </a>
                <a href={registerUrl} className="tels-btn tels-btn--primary tels-btn--sm">
                  {intl.formatMessage(telsHeaderMessages.register)}
                </a>
              </>
            )}
          </div>

          <button
            type="button"
            className="tels-header__mobile"
            aria-label={intl.formatMessage(telsHeaderMessages.menu)}
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((open) => !open)}
          >
            <FontAwesomeIcon icon={mobileOpen ? faTimes : faBars} />
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="tels-header__mobile-panel">
          {navItems.map((item) => renderNavItemLink(item, {
            key: `mobile-${item.titleKey}-${item.urlKey}`,
            onClick: closeMobile,
          }))}
          {authenticatedUser ? (
            <>
              {profileUrl && (
                <a href={profileUrl} onClick={closeMobile}>
                  {intl.formatMessage(telsHeaderMessages.profile)}
                </a>
              )}
              {accountUrl && (
                <a href={accountUrl} onClick={closeMobile}>
                  {intl.formatMessage(telsHeaderMessages.account)}
                </a>
              )}
              <a href={logoutUrl} onClick={closeMobile}>
                {intl.formatMessage(telsHeaderMessages.logout)}
              </a>
            </>
          ) : (
            <>
              <a
                href={loginUrl}
                className="tels-btn tels-btn--ghost tels-btn--sm"
                onClick={closeMobile}
              >
                {intl.formatMessage(telsHeaderMessages.signIn)}
              </a>
              <a
                href={registerUrl}
                className="tels-btn tels-btn--primary tels-btn--sm"
                onClick={closeMobile}
              >
                {intl.formatMessage(telsHeaderMessages.register)}
              </a>
            </>
          )}
        </div>
      )}
    </header>
  );
};
