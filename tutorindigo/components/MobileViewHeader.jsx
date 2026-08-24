const MobileViewHeader = () => {
  const config = getConfig();
  const intl = useIntl();
  const messages = {
    "mobile.view.header.logo.altText": {
      id: "mobile.view.header.logo.altText",
      defaultMessage: "My Open edX",
      description: "alt text for the mobile view header logo",
    },
  };

  const BASE_URL = config.LMS_BASE_URL;
  const logoUrl =
    config.LOGO_URL || `${BASE_URL}/theming/asset/images/logo.png`;
  const logoWhiteUrl =
    config.LOGO_WHITE_URL || `${BASE_URL}/theming/asset/images/logo-white.png`;

  return (
    <>
      <style>
        {`
          #root .logo-image.logo-white {
            display: none;
          }
          [data-paragon-theme-variant="dark"] #root .logo-image {
            display: none;
          }
          [data-paragon-theme-variant="dark"] #root .logo-white {
            display: block;
          }
        `}
      </style>
      <div className="d-flex align-items-center justify-content-between w-100">
        <a href={`${BASE_URL}/dashboard`} title="Home" className="logo">
          <img className="logo-image" src={logoUrl} alt={intl.formatMessage(messages["mobile.view.header.logo.altText"])} />
          <img className="logo-image logo-white" src={logoWhiteUrl} alt={intl.formatMessage(messages["mobile.view.header.logo.altText"])} />
        </a>
        <HeaderControls />
      </div>
    </>
  );
};
