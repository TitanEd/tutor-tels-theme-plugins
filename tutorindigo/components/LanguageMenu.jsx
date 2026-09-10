const languageMenuMessages = defineMessages({
  language: {
    id: 'tels.header.language.label',
    defaultMessage: 'Language',
    description: 'Header language selector label',
  },
});

const LanguageMenu = () => {
  const intl = useIntl();
  const config = getConfig();
  const languages = config.INDIGO_SUPPORTED_LANGUAGES || [];
  const enableLanguageMenu = config.INDIGO_ENABLE_LANGUAGE_MENU !== false;

  if (!enableLanguageMenu || languages.length < 2) {
    return null;
  }

  const cookies = new Cookies();
  const cookieName = config.LANGUAGE_PREFERENCE_COOKIE_NAME || 'openedx-language-preference';
  const serverURL = new URL(config.LMS_BASE_URL);
  const currentLocale = (intl.locale || 'en').toLowerCase();
  const selectedValue = languages.find((lang) => lang.value.toLowerCase() === currentLocale)?.value
    || languages.find((lang) => currentLocale.startsWith(lang.value.toLowerCase()))?.value
    || languages[0].value;

  const onChange = (event) => {
    cookies.set(cookieName, event.target.value, {
      path: '/',
      domain: serverURL.hostname,
      expires: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
      sameSite: 'lax',
    });
    window.location.reload();
  };

  // Visual design: tels-brand-openedx/paragon/_header.scss (form tokens).
  return (
    <div className="indigo-language-menu">
      <label htmlFor="indigo-header-language-select" className="sr-only">
        {intl.formatMessage(languageMenuMessages.language)}
      </label>
      <select
        id="indigo-header-language-select"
        className="form-control form-control-sm"
        value={selectedValue}
        onChange={onChange}
        aria-label={intl.formatMessage(languageMenuMessages.language)}
      >
        {languages.map(({ value, label }) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
    </div>
  );
};
