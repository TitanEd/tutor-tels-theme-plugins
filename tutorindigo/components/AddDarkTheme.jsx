let themeVariant = 'selected-paragon-theme-variant';

// Footer widget: marks the page as dark as soon as it mounts, so the dark stylesheet applies while
// the rest of the app is still loading. Starting in the chosen variant and styling the iframes of a
// dark page are done once per page load in ThemeVariantSync.jsx (above), for every MFE, including
// the ones embedded without a footer.
const AddDarkTheme = () => {
  const isThemeToggleEnabled = getConfig().INDIGO_ENABLE_DARK_TOGGLE;

  useEffect(() => {
    const theme = window.localStorage.getItem(themeVariant);

    if (isThemeToggleEnabled && theme === 'dark') {
      document.documentElement.setAttribute('data-paragon-theme-variant', 'dark');
    }
  }, []);

  return (<div />);
};
