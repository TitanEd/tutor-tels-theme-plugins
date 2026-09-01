/**
 * Shared marketing header (PLUGIN_SLOTS widget id: custom_header /
 * custom_header_desktop / custom_header_mobile). Slot *ids* differ by MFE —
 * see HEADER_REPLACEMENT_SLOTS in plugin.py. Do not reuse one slot id across
 * header families (public header.v1 vs desktop vs learning).
 *
 * Logged out: Home | Courses | About Us | Contact + Sign In / Register
 * Logged in:  Home | Dashboard | Courses | About Us | Contact + user menu
 * Styles: tels-brand-openedx .custom-header* / .tels-btn* (tokens only).
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

const customHeaderMessages = defineMessages({
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
  controlHub: {
    id: 'account.user.menu.control.hub',
    defaultMessage: 'Control Hub',
    description: 'Control Hub link label in the user menu (admin only)',
  },
  studio: {
    id: 'account.user.menu.studio',
    defaultMessage: 'Studio',
    description: 'Studio link label in the user menu (admin only)',
  },
  logout: {
    id: 'tels.header.user.logout',
    defaultMessage: 'Sign Out',
    description: 'User dropdown Sign Out link',
  },
});

const CustomHeader = () => {
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
  const studioUrl = config.STUDIO_BASE_URL;
  const controlHubUrl = `${config.LMS_BASE_URL}/control-hub`;
  const canSeePrivilegedItems = authenticatedUser?.administrator === true;
  const isPublicMfe = process.env.APP_ID === 'public';
  const guestNav = config.INDIGO_HEADER_GUEST_NAV || DEFAULT_GUEST_NAV;
  const authNav = config.INDIGO_HEADER_AUTH_NAV || DEFAULT_AUTH_NAV;
  const navItems = authenticatedUser ? authNav : guestNav;
  const location = useLocation();

  const userMenuLinks = authenticatedUser ? [
    profileUrl && {
      key: 'profile',
      href: profileUrl,
      message: customHeaderMessages.profile,
    },
    accountUrl && {
      key: 'account',
      href: accountUrl,
      message: customHeaderMessages.account,
    },
    {
      key: 'dashboard',
      href: dashboardUrl,
      message: customHeaderMessages.dashboard,
    },
    canSeePrivilegedItems && {
      key: 'control-hub',
      href: controlHubUrl,
      message: customHeaderMessages.controlHub,
    },
    canSeePrivilegedItems && studioUrl && {
      key: 'studio',
      href: studioUrl,
      message: customHeaderMessages.studio,
    },
    {
      key: 'logout',
      href: logoutUrl,
      message: customHeaderMessages.logout,
    },
  ].filter(Boolean) : [];

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
    if (titleKey in customHeaderMessages) {
      return intl.formatMessage(customHeaderMessages[titleKey]);
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
    const navClass = ['custom-header__nav-link', className].filter(Boolean).join(' ');
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
  const closeUserMenu = () => setUserMenuOpen(false);

  return (
    <header className="custom-header">
      <div className="tels-container">
        <div className="custom-header__row">
          <a
            href={homeUrl}
            className="custom-header__logo"
            aria-label={intl.formatMessage(customHeaderMessages.homeAria, { siteName })}
          >
            <img src={logoUrl} alt={siteName} />
          </a>

          <nav className="custom-header__nav" aria-label={intl.formatMessage(customHeaderMessages.primaryNav)}>
            {navItems.map((item) => renderNavItemLink(item, {
              key: `${item.titleKey}-${item.urlKey}`,
            }))}
          </nav>

          <div className="custom-header__actions">
            {authenticatedUser ? (
              <div className="custom-header__user" ref={userMenuRef}>
                <button
                  type="button"
                  className="custom-header__user-toggle"
                  aria-label={intl.formatMessage(customHeaderMessages.userMenu)}
                  aria-expanded={userMenuOpen}
                  onClick={() => setUserMenuOpen((open) => !open)}
                >
                  <span className="custom-header__user-name">
                    {authenticatedUser.name || authenticatedUser.username}
                  </span>
                  <FontAwesomeIcon icon={faChevronDown} aria-hidden="true" />
                </button>
                {userMenuOpen && (
                  <ul className="custom-header__user-menu">
                    {userMenuLinks.map((item) => (
                      <li key={item.key}>
                        <a href={item.href} onClick={closeUserMenu}>
                          {intl.formatMessage(item.message)}
                        </a>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ) : (
              <>
                <a href={loginUrl} className="tels-btn tels-btn--ghost tels-btn--sm">
                  {intl.formatMessage(customHeaderMessages.signIn)}
                </a>
                <a href={registerUrl} className="tels-btn tels-btn--primary tels-btn--sm">
                  {intl.formatMessage(customHeaderMessages.register)}
                </a>
              </>
            )}
          </div>

          <button
            type="button"
            className="custom-header__mobile"
            aria-label={intl.formatMessage(customHeaderMessages.menu)}
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((open) => !open)}
          >
            <FontAwesomeIcon icon={mobileOpen ? faTimes : faBars} />
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="custom-header__mobile-panel">
          {navItems.map((item) => renderNavItemLink(item, {
            key: `mobile-${item.titleKey}-${item.urlKey}`,
            onClick: closeMobile,
          }))}
          {authenticatedUser ? (
            userMenuLinks.map((item) => (
              <a key={`mobile-${item.key}`} href={item.href} onClick={closeMobile}>
                {intl.formatMessage(item.message)}
              </a>
            ))
          ) : (
            <>
              <a
                href={loginUrl}
                className="tels-btn tels-btn--ghost tels-btn--sm"
                onClick={closeMobile}
              >
                {intl.formatMessage(customHeaderMessages.signIn)}
              </a>
              <a
                href={registerUrl}
                className="tels-btn tels-btn--primary tels-btn--sm"
                onClick={closeMobile}
              >
                {intl.formatMessage(customHeaderMessages.register)}
              </a>
            </>
          )}
        </div>
      )}
    </header>
  );
};
