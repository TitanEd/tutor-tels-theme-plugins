// The header of the site template in use (SiteTemplate.jsx). Registry of the templates this plugin ships:
// add a template by adding its header component and an entry here (and its footer in SiteFooter.jsx).
const SITE_TEMPLATE_HEADERS = {
  'template-1': CustomHeader,
  'template-2': Template2Header,
};

const SiteHeader = () => {
  const config = getConfig();
  const { template, known } = useSiteTemplate();
  if (!known) {
    return null; // first visit without a cookie: wait for the LMS answer instead of flashing another template
  }
  const Header = SITE_TEMPLATE_HEADERS[template] || SITE_TEMPLATE_HEADERS[config.INDIGO_SITE_TEMPLATE_DEFAULT] || CustomHeader;
  return <Header />;
};
