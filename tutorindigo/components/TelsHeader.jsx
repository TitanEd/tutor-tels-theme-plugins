/**
 * Shared marketing header for MFEs that mount HeaderSlot
 * (PLUGIN_SLOTS → org.openedx.frontend.layout.header.v1).
 * Template B (Harvard-PLL / tels-mirror): sticky header that's transparent
 * over the public MFE's home hero (solid on scroll), solid dark on the
 * catalog/subject/school pages, white everywhere else — hamburger opens a
 * full-bleed dark "Browse by Subject Area" mega-menu; "View all courses"
 * pill on the left; centered logo. No search bar/logic (product decision).
 * Styles: tels-brand-openedx .tels-header* / .tels-btn* (tokens only).
 */

const SUBJECTS = [
  'Art & Design',
  'Business',
  'Computer Science',
  'Data Science',
  'Education & Teaching',
  'Health & Medicine',
  'Humanities',
  'Mathematics',
  'Programming',
  'Science',
  'Social Sciences',
  'Theology',
];

const SUBJECT_ICONS = {
  'Art & Design': faPalette,
  Business: faBriefcase,
  'Computer Science': faCode,
  'Data Science': faDatabase,
  'Education & Teaching': faGraduationCap,
  'Health & Medicine': faHeartbeat,
  Humanities: faUsers,
  Mathematics: faSquareRootAlt,
  Programming: faLaptopCode,
  Science: faFlask,
  'Social Sciences': faGlobe,
  Theology: faBookOpen,
};

const telsHeaderMessages = defineMessages({
  homeAria: {
    id: 'tels.header.logo.aria',
    defaultMessage: '{siteName} Home',
    description: 'Aria label for header logo home link',
  },
  menu: {
    id: 'tels.header.mobile.menu',
    defaultMessage: 'Menu',
    description: 'Hamburger menu toggle aria label',
  },
  viewAllCourses: {
    id: 'tels.header.viewAllCourses',
    defaultMessage: 'View all courses',
    description: 'Header "View all courses" button',
  },
  browseBySubject: {
    id: 'tels.header.browseBySubject',
    defaultMessage: 'Browse by Subject Area',
    description: 'Subject mega-menu heading',
  },
});

const TelsHeader = () => {
  const intl = useIntl();
  const config = getConfig();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  const siteName = config.SITE_NAME || 'TitanEd';
  const logoUrl = config.LOGO_URL || `${config.LMS_BASE_URL}/theming/asset/images/logo.png`;

  const homeUrl = config.INDIGO_HOME_URL || config.MARKETING_SITE_BASE_URL || config.BASE_URL || '/public/';
  const coursesUrl = config.INDIGO_COURSES_URL || `${String(homeUrl).replace(/\/$/, '')}/courses`;
  const catalogUrl = config.INDIGO_CATALOG_URL || `${String(homeUrl).replace(/\/$/, '')}/catalog`;

  const isPublicMfe = process.env.APP_ID === 'public';
  const pathname = location?.pathname || '';
  const isHome = isPublicMfe && (pathname === '/' || pathname === '');
  const isCatalog = isPublicMfe
    && (pathname.startsWith('/catalog') || pathname.startsWith('/subject/') || pathname.startsWith('/school/'));

  useEffect(() => {
    if (!isHome) {
      return undefined;
    }
    const onScroll = () => setScrolled(window.scrollY > 10);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [isHome]);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [menuOpen]);

  useEffect(() => { setMenuOpen(false); }, [pathname]);

  let variant = 'light';
  if (menuOpen || isCatalog) {
    variant = 'dark';
  } else if (isHome) {
    variant = scrolled ? 'dark' : 'transparent';
  }

  const closeMenu = () => setMenuOpen(false);

  return (
    <>
      <header className={`tels-header ${variant === 'dark' ? 'tels-header--dark' : ''} ${variant === 'light' ? 'tels-header--light' : ''}`}>
        <div className="tels-container">
          <div className="tels-header__row">
            <div className="tels-header__start">
              <button
                type="button"
                className="tels-header__menu-btn"
                onClick={() => setMenuOpen((open) => !open)}
                aria-label={intl.formatMessage(telsHeaderMessages.menu)}
                aria-expanded={menuOpen}
              >
                <FontAwesomeIcon icon={menuOpen ? faTimes : faBars} />
              </button>
              <NavLink to={catalogUrl.startsWith('http') ? undefined : catalogUrl} className="tels-header__view-all">
                {intl.formatMessage(telsHeaderMessages.viewAllCourses)}
              </NavLink>
            </div>

            <NavLink
              to={homeUrl.startsWith('http') ? undefined : homeUrl}
              className="tels-header__logo"
              aria-label={intl.formatMessage(telsHeaderMessages.homeAria, { siteName })}
            >
              <img src={logoUrl} alt={siteName} />
            </NavLink>
          </div>
        </div>
      </header>

      {menuOpen && (
        <div className="tels-header__menu">
          <div className="tels-container tels-header__menu-inner">
            <h2 className="tels-header__menu-title">
              {intl.formatMessage(telsHeaderMessages.browseBySubject)}
            </h2>
            <ul className="tels-header__subjects">
              {SUBJECTS.map((subject) => (
                <li key={subject}>
                  <NavLink
                    to={`${catalogUrl}?subject=${encodeURIComponent(subject)}`}
                    className="tels-header__subject-link"
                    onClick={closeMenu}
                  >
                    <FontAwesomeIcon icon={SUBJECT_ICONS[subject] || faBookOpen} />
                    <span>{subject}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </>
  );
};
