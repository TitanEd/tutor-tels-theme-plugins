/**
 * Shared marketing header (PLUGIN_SLOTS widget id: custom_header /
 * custom_header_desktop / custom_header_mobile). Slot *ids* differ by MFE —
 * see HEADER_REPLACEMENT_SLOTS in plugin.py. Do not reuse one slot id across
 * header families (public header.v1 vs desktop vs learning).
 * Template B (Harvard-PLL / tels-mirror): sticky header is the same chrome
 * on every page — solid dark navy, except transparent over the public MFE
 * home hero until the user scrolls. Hamburger opens a "Browse by Subject
 * Area" mega-menu; centered logo. No search bar/logic (product decision).
 * "View all courses" (left, next to the hamburger) is a filter-reset
 * control, not a nav link — only rendered on the catalog listing page while
 * a filter is applied (i.e. the URL has a query string), and points at the
 * bare catalog URL so clicking it drops every filter.
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

const customHeaderMessages = defineMessages({
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
  close: {
    id: 'tels.header.mobile.close',
    defaultMessage: 'Close menu',
    description: 'Hamburger menu close aria label',
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
  artDesign: {
    id: 'tels.taxonomy.subject.artDesign',
    defaultMessage: 'Art & Design',
    description: 'Subject area name',
  },
  business: {
    id: 'tels.taxonomy.subject.business',
    defaultMessage: 'Business',
    description: 'Subject area name',
  },
  computerScience: {
    id: 'tels.taxonomy.subject.computerScience',
    defaultMessage: 'Computer Science',
    description: 'Subject area name',
  },
  dataScience: {
    id: 'tels.taxonomy.subject.dataScience',
    defaultMessage: 'Data Science',
    description: 'Subject area name',
  },
  educationTeaching: {
    id: 'tels.taxonomy.subject.educationTeaching',
    defaultMessage: 'Education & Teaching',
    description: 'Subject area name',
  },
  healthMedicine: {
    id: 'tels.taxonomy.subject.healthMedicine',
    defaultMessage: 'Health & Medicine',
    description: 'Subject area name',
  },
  humanities: {
    id: 'tels.taxonomy.subject.humanities',
    defaultMessage: 'Humanities',
    description: 'Subject area name',
  },
  mathematics: {
    id: 'tels.taxonomy.subject.mathematics',
    defaultMessage: 'Mathematics',
    description: 'Subject area name',
  },
  programming: {
    id: 'tels.taxonomy.subject.programming',
    defaultMessage: 'Programming',
    description: 'Subject area name',
  },
  science: {
    id: 'tels.taxonomy.subject.science',
    defaultMessage: 'Science',
    description: 'Subject area name',
  },
  socialSciences: {
    id: 'tels.taxonomy.subject.socialSciences',
    defaultMessage: 'Social Sciences',
    description: 'Subject area name',
  },
  theology: {
    id: 'tels.taxonomy.subject.theology',
    defaultMessage: 'Theology',
    description: 'Subject area name',
  },
});

const SUBJECT_MESSAGE_KEY = {
  'Art & Design': 'artDesign',
  Business: 'business',
  'Computer Science': 'computerScience',
  'Data Science': 'dataScience',
  'Education & Teaching': 'educationTeaching',
  'Health & Medicine': 'healthMedicine',
  Humanities: 'humanities',
  Mathematics: 'mathematics',
  Programming: 'programming',
  Science: 'science',
  'Social Sciences': 'socialSciences',
  Theology: 'theology',
};

const CustomHeader = () => {
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

  // "View all courses" only appears on the catalog listing page, and only
  // once a filter is actually applied — it's a reset control, not general
  // nav. Linking to the bare catalog URL (no query string) is the reset:
  // the catalog page reads its filters from the query string, so landing
  // there with none applied shows every course again.
  const hasActiveCatalogFilters = isPublicMfe
    && pathname.startsWith('/catalog')
    && !!(location?.search && location.search.length > 1);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [menuOpen]);

  useEffect(() => { setMenuOpen(false); }, [pathname]);

  const overHomeHero = isHome && !scrolled && !menuOpen;
  const variant = overHomeHero ? 'transparent' : 'dark';

  const closeMenu = () => setMenuOpen(false);

  return (
    <>
      <header className={`tels-header${variant === 'dark' ? ' tels-header--dark' : ''}`}>
        <div className="tels-container">
          <div className="tels-header__row">
            <div className="tels-header__start">
              <button
                type="button"
                className="tels-header__menu-btn"
                onClick={() => setMenuOpen((open) => !open)}
                aria-label={intl.formatMessage(menuOpen ? customHeaderMessages.close : customHeaderMessages.menu)}
                aria-expanded={menuOpen}
                aria-controls="tels-header-menu"
              >
                <FontAwesomeIcon icon={menuOpen ? faTimes : faBars} />
              </button>
              {hasActiveCatalogFilters && (
                <NavLink to={catalogUrl.startsWith('http') ? undefined : catalogUrl} className="tels-header__view-all">
                  {intl.formatMessage(customHeaderMessages.viewAllCourses)}
                </NavLink>
              )}
            </div>

            <NavLink
              to={homeUrl.startsWith('http') ? undefined : homeUrl}
              className="tels-header__logo"
              aria-label={intl.formatMessage(customHeaderMessages.homeAria, { siteName })}
            >
              <img src={logoUrl} alt={siteName} />
            </NavLink>
          </div>
        </div>
      </header>

      <div
        id="tels-header-menu"
        className={`tels-header__menu${menuOpen ? ' tels-header__menu--open' : ''}`}
        aria-hidden={!menuOpen}
      >
        <div className="tels-header__menu-clip">
          <div className="tels-container tels-header__menu-inner">
            <h2 className="tels-header__menu-title">
              {intl.formatMessage(customHeaderMessages.browseBySubject)}
            </h2>
            <ul className="tels-header__subjects">
              {SUBJECTS.map((subject) => (
                <li key={subject}>
                  <NavLink
                    to={`${catalogUrl}?subject=${encodeURIComponent(subject)}`}
                    className="tels-header__subject-link"
                    onClick={closeMenu}
                    tabIndex={menuOpen ? 0 : -1}
                  >
                    <FontAwesomeIcon icon={SUBJECT_ICONS[subject] || faBookOpen} />
                    <span>
                      {intl.formatMessage(customHeaderMessages[SUBJECT_MESSAGE_KEY[subject]])}
                    </span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </>
  );
};
