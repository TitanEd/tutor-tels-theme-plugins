
const ThemedLogo = () => {
  const config = getConfig();
  const BASE_URL = config.LMS_BASE_URL;
  // Live branding (control-panel ui_configuration) serves the admin-uploaded logos.
  const logoUrl = (config.INDIGO_LIVE_BRANDING && config.LOGO_URL) || `${BASE_URL}/static/indigo/images/logo.png`;
  const logoWhiteUrl = (config.INDIGO_LIVE_BRANDING && config.LOGO_WHITE_URL) || `${BASE_URL}/static/indigo/images/logo-white.png`;

  return (
    <>
      <style>
        {`
          #root header .logo-image.logo-white {
            display: none;
          }
          [data-paragon-theme-variant="dark"] #root header .logo-image {
            display: none;
          }
          [data-paragon-theme-variant="dark"] #root header .logo-white {
            display: block;
          }
        `}
      </style>
      <a href={`${BASE_URL}/dashboard`} title="Open edX" className="logo">
        <img className="logo-image" src={logoUrl} alt="Open edX" />
        <img className="logo-image logo-white" src={logoWhiteUrl} alt="Open edX" />
      </a>
    </>
  );
};
