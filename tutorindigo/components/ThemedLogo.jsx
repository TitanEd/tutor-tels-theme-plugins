const ThemedLogo = () => {
  const config = getConfig();
  const BASE_URL = config.LMS_BASE_URL;
  // Prefer MFE_CONFIG / theming assets (tels_brand_image) over hardcoded Indigo paths.
  const logoUrl =
    config.LOGO_URL || `${BASE_URL}/theming/asset/images/logo.png`;
  const logoWhiteUrl =
    config.LOGO_WHITE_URL || `${BASE_URL}/theming/asset/images/logo-white.png`;

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
      <a href={`${BASE_URL}/dashboard`} title="Home" className="logo">
        <img className="logo-image" src={logoUrl} alt="Home" />
        <img className="logo-image logo-white" src={logoWhiteUrl} alt="Home" />
      </a>
    </>
  );
};
