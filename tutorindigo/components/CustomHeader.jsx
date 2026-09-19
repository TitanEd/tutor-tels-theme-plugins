/**
 * Shared marketing header (PLUGIN_SLOTS widget id: custom_header /
 * custom_header_desktop / custom_header_mobile). Slot *ids* differ by MFE —
 * see HEADER_REPLACEMENT_SLOTS in plugin.py. Do not reuse one slot id across
 * header families (public header.v1 vs desktop vs learning).
 * Template B (Harvard-PLL): sticky header — solid dark navy except transparent
 * over the public MFE home hero until scroll. Hamburger opens "Browse by Subject
 * Area"; centered logo; right-side catalog search → /courses?keywords=…;
 * language selector in the mega-menu (same chrome as public MFE TelsHeader).
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
  logoAlt: {
    id: 'tels.header.logo.alt',
    defaultMessage: '{siteName}',
    description: 'Header logo image alt text',
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
  searchLabel: {
    id: 'tels.header.search.label',
    defaultMessage: 'Search',
    description: 'Visually hidden label for header catalog search',
  },
  searchPlaceholder: {
    id: 'tels.header.search.placeholder',
    defaultMessage: 'Search',
    description: 'Placeholder for header catalog search input',
  },
  searchSubmit: {
    id: 'tels.header.search.submit',
    defaultMessage: 'Apply search',
    description: 'Aria label for header search submit / icon button',
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

/** In-app NavLink on the public MFE; full page <a> everywhere else (cross-port).
 *  href is the real browser URL (/public, /public/courses?subject=…).
 *  NavLink gets the basename-relative path so it never becomes /public/public. */
const ChromeLink = ({ href, className, children, ...rest }) => {
  const inPublicApp = process.env.APP_ID === 'public';
  if (inPublicApp && href && !href.startsWith('//')) {
    const to = toPublicAppPath(href);
    if (to && !to.startsWith('http://') && !to.startsWith('https://')) {
      return <NavLink to={to} className={className} {...rest}>{children}</NavLink>;
    }
  }
  return <a href={href} className={className} {...rest}>{children}</a>;
};

const CustomHeader = () => {
  const intl = useIntl();
  const config = getConfig();
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [searchQuery, setSearchQuery] = useState(() => {
    try {
      return new URLSearchParams(location.search).get('keywords') || '';
    } catch {
      return '';
    }
  });

  const siteName = config.SITE_NAME || 'TitanEd';
  const logoUrl = config.LOGO_URL || `${config.LMS_BASE_URL}/theming/asset/images/logo.png`;

  const isPublicMfe = process.env.APP_ID === 'public';
  const homeUrl = publicHomeHref(config);
  const coursesUrl = resolvePublicMfeUrl('/courses', config);

  const pathname = location?.pathname || '';
  const isHome = isPublicMfe && (pathname === '/' || pathname === '');
  // Same chrome as public MFE: hide “View all courses” only on the public home hero.
  const showViewAllCourses = !(isPublicMfe && isHome);

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

  useEffect(() => {
    try {
      setSearchQuery(new URLSearchParams(location.search).get('keywords') || '');
    } catch {
      setSearchQuery('');
    }
  }, [location.search]);

  const overHomeHero = isHome && !scrolled && !menuOpen;
  const variant = overHomeHero ? 'transparent' : 'dark';

  const closeMenu = () => setMenuOpen(false);

  const goToCourseSearch = (rawQuery) => {
    const keywords = String(rawQuery || '').trim();
    if (isPublicMfe) {
      navigate(keywords
        ? `/courses?keywords=${encodeURIComponent(keywords)}`
        : '/courses');
      return;
    }
    window.location.assign(publicCoursesHref(config, keywords ? { keywords } : {}));
  };

  const onSearchSubmit = (event) => {
    event.preventDefault();
    goToCourseSearch(searchQuery);
  };

  return (
    <>
      <header className={`tels-header${variant === 'dark' ? ' tels-header--dark' : ''}`}>
        <div className="tels-container">
          <div className="tels-header__row">
            <div className="tels-header__start">
              <button
                type="button"
                className={`tels-header__menu-btn${menuOpen ? ' is-open' : ''}`}
                onClick={() => setMenuOpen((open) => !open)}
                aria-label={intl.formatMessage(menuOpen ? customHeaderMessages.close : customHeaderMessages.menu)}
                aria-expanded={menuOpen}
                aria-controls="tels-header-menu"
              >
                <span />
                <span />
                <span />
              </button>
              {showViewAllCourses && (
                <ChromeLink href={coursesUrl} className="tels-header__view-all">
                  {intl.formatMessage(customHeaderMessages.viewAllCourses)}
                </ChromeLink>
              )}
            </div>

            <a
              href={homeUrl}
              className="tels-header__logo"
              aria-label={intl.formatMessage(customHeaderMessages.homeAria, { siteName })}
            >
              <img
                src={logoUrl}
                alt={intl.formatMessage(customHeaderMessages.logoAlt, { siteName })}
              />
            </a>

            <div className="tels-header__end">
              <form
                className="tels-header__search"
                role="search"
                onSubmit={onSearchSubmit}
                action={coursesUrl}
                method="get"
              >
                <label className="sr-only" htmlFor="tels-header-search">
                  {intl.formatMessage(customHeaderMessages.searchLabel)}
                </label>
                <input
                  id="tels-header-search"
                  className="tels-header__search-input"
                  type="text"
                  name="keywords"
                  placeholder={intl.formatMessage(customHeaderMessages.searchPlaceholder)}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  autoComplete="off"
                  maxLength={128}
                />
                <button
                  type="submit"
                  className="tels-header__search-submit"
                  aria-label={intl.formatMessage(customHeaderMessages.searchSubmit)}
                >
                  {/* Same lucide Search path/stroke as public MFE TelsHeader — brand CSS sizes via .tels-header__search-submit svg */}
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="35"
                    height="35"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3.25"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.3-4.3" />
                  </svg>
                </button>
              </form>
            </div>
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
                  <ChromeLink
                    href={publicCoursesHref(config, { subject })}
                    className="tels-header__subject-link"
                    onClick={closeMenu}
                    tabIndex={menuOpen ? 0 : -1}
                  >
                    <FontAwesomeIcon icon={SUBJECT_ICONS[subject] || faBookOpen} />
                    <span>
                      {intl.formatMessage(customHeaderMessages[SUBJECT_MESSAGE_KEY[subject]])}
                    </span>
                  </ChromeLink>
                </li>
              ))}
            </ul>
            <div className="tels-header__menu-lang">
              <LanguageMenu />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
