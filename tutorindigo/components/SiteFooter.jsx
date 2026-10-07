// The footer of the site template in use (SiteTemplate.jsx); see SiteHeader.jsx for the registry.
const SITE_TEMPLATE_FOOTERS = {
  'template-1': IndigoFooter,
  'template-2': Template2Footer,
};

const SiteFooter = () => {
  const config = getConfig();
  const { template, known } = useSiteTemplate();
  if (!known) {
    return null;
  }
  const Footer = SITE_TEMPLATE_FOOTERS[template] || SITE_TEMPLATE_FOOTERS[config.INDIGO_SITE_TEMPLATE_DEFAULT] || IndigoFooter;
  return <Footer />;
};
