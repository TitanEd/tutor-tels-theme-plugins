const ToggleThemeButton = () => {
  const intl = useIntl();
  const themeCookie = 'selected-paragon-theme-variant';
  const themeCookieExpiry = 90; // days
  const isThemeToggleEnabled = getConfig().INDIGO_ENABLE_DARK_TOGGLE;
  const initialDark = typeof document !== 'undefined'
    && document.cookie.split('; ').find((row) => row.startsWith(`${themeCookie}=`))?.split('=')[1] === 'dark';
  const [isDarkThemeEnabled, setIsDarkThemeEnabled] = useState(initialDark);

  const getCookie = (name) => document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
    ?.split('=')[1];

  const setCookie = (name, value, { domain, path, expires }) => {
    document.cookie = `${name}=${value}; domain=${domain}; path=${path}; expires=${expires.toUTCString()}; SameSite=Lax`;
  };

  const serverURL = new URL(getConfig().LMS_BASE_URL);

  const getCookieExpiry = () => {
    const today = new Date();
    return new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate() + themeCookieExpiry,
    );
  };

  const getCookieOptions = (url) => ({
    domain: url.hostname,
    path: '/',
    expires: getCookieExpiry(),
  });

  const onToggleTheme = () => {
    const nextIsDark = getCookie(themeCookie) !== 'dark';
    const theme = nextIsDark ? 'dark' : 'light';

    document.documentElement.setAttribute('data-paragon-theme-variant', theme);
    setIsDarkThemeEnabled(nextIsDark);
    window.localStorage.setItem(themeCookie, theme);
    setTimeout(() => {
      setCookie(themeCookie, theme, getCookieOptions(serverURL));
      window.location.reload();
    }, 1);
  };

  useEffect(() => {
    const cookieTheme = getCookie(themeCookie);
    if (!cookieTheme || cookieTheme === 'undefined') {
      return;
    }
    if (cookieTheme !== window.localStorage.getItem(themeCookie)) {
      window.localStorage.setItem(themeCookie, cookieTheme);
      window.location.reload();
    }
    setIsDarkThemeEnabled(cookieTheme === 'dark');
  }, []);

  if (!isThemeToggleEnabled) {
    return null;
  }

  const label = intl.formatMessage({
    id: 'header.user.theme',
    defaultMessage: 'Toggle theme',
    description: 'Toggle between light and dark theme',
  });

  // Visual design: tels-brand-openedx/paragon/_header.scss (design tokens).
  return (
    <div className="indigo-theme-toggle" title={label}>
      <span className="indigo-theme-toggle__icon" aria-hidden="true">
        <Icon src={WbSunny} />
      </span>
      <label className="indigo-theme-toggle__switch" htmlFor="indigo-theme-toggle-input">
        <input
          id="indigo-theme-toggle-input"
          type="checkbox"
          role="switch"
          checked={isDarkThemeEnabled}
          onChange={onToggleTheme}
          aria-label={label}
        />
        <span className="indigo-theme-toggle__slider" />
      </label>
      <span className="indigo-theme-toggle__icon" aria-hidden="true">
        <Icon src={Nightlight} />
      </span>
    </div>
  );
};
