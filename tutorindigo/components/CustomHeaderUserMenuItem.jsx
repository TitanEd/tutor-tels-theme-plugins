/**
 * Desktop + mobile user-menu dropdown contents
 * (org.openedx.frontend.layout.header_desktop_user_menu.v1 /
 * header_mobile_user_menu.v1). Same items and admin/non-admin gating as the
 * reference theme: everyone gets Dashboard/Profile/Account/Sign out; users
 * with `authenticatedUser.administrator` also get Control Hub, plus Studio
 * when the MFE's config exposes STUDIO_BASE_URL.
 *
 * Message ids intentionally reuse @edx/frontend-component-header's own
 * catalog ids (account.user.menu.*) rather than a tels.* namespace — every
 * locale Open edX already ships a translation for these exact labels (they
 * back the header's own default dashboard/profile/sign-out links), so this
 * dropdown is fully translated with no extra i18n work.
 */
const hasElevatedMenuAccess = (authenticatedUser) => authenticatedUser?.administrator === true;

const userMenuItemMessages = defineMessages({
  dashboard: {
    id: 'account.user.menu.dashboard',
    defaultMessage: 'Dashboard',
    description: 'Dashboard link label in the user menu',
  },
  profile: {
    id: 'account.user.menu.profile',
    defaultMessage: 'Profile',
    description: 'Profile link label in the user menu',
  },
  account: {
    id: 'account.user.menu.account',
    defaultMessage: 'Account',
    description: 'Account settings link label in the user menu',
  },
  controlHub: {
    id: 'account.user.menu.control.hub',
    defaultMessage: 'Control Hub',
    description: 'Control Hub link label in the user menu (admin only)',
  },
  studio: {
    id: 'account.user.menu.studio',
    defaultMessage: 'Studio',
    description: 'Studio link label in the user menu (admin only)',
  },
  signout: {
    id: 'account.user.menu.signout',
    defaultMessage: 'Sign out',
    description: 'Sign out link label in the user menu',
  },
});

const CustomHeaderUserMenuItem = () => {
  const intl = useIntl();
  const { authenticatedUser, config } = useContext(AppContext);
  const username = authenticatedUser?.username;
  const canSeePrivilegedItems = hasElevatedMenuAccess(authenticatedUser);
  const studioUrl = config.STUDIO_BASE_URL;

  const items = [
    {
      key: 'dashboard',
      content: intl.formatMessage(userMenuItemMessages.dashboard),
      href: `${config.LMS_BASE_URL}/dashboard`,
    },
    {
      key: 'profile',
      content: intl.formatMessage(userMenuItemMessages.profile),
      href: `${config.ACCOUNT_PROFILE_URL}/u/${username}`,
    },
    {
      key: 'account',
      content: intl.formatMessage(userMenuItemMessages.account),
      href: config.ACCOUNT_SETTINGS_URL,
    },
    ...(canSeePrivilegedItems ? [
      {
        key: 'control-hub',
        content: intl.formatMessage(userMenuItemMessages.controlHub),
        href: `${config.LMS_BASE_URL}/control-hub`,
      },
      ...(studioUrl ? [{
        key: 'studio',
        content: intl.formatMessage(userMenuItemMessages.studio),
        href: studioUrl,
      }] : []),
    ] : []),
    {
      key: 'signout',
      content: intl.formatMessage(userMenuItemMessages.signout),
      href: config.LOGOUT_URL,
    },
  ];

  return (
    <>
      {items.map((item) => (
        <a key={item.key} className="dropdown-item" href={item.href}>
          {item.content}
        </a>
      ))}
    </>
  );
};
