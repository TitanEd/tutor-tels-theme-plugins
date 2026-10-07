/**
 * Header user-menu "toggle" trigger — the avatar + display name + chevron
 * button that opens the account dropdown
 * (org.openedx.frontend.layout.header_desktop_user_menu_toggle.v1).
 * Same visual pattern as the reference theme (VigyanShaala's tutor-indigo
 * plugin): the learner's own photo when they have one, a generic account
 * icon otherwise.
 *
 * Styles: .tels-user-menu-toggle-* rules in tels-brand-openedx's
 * paragon/_header.scss (design tokens — var(--pgn-color-*) with hex
 * fallbacks), not injected here — keeps this file's own concern to markup
 * + behavior, and the CSS ships compiled with the rest of the header's
 * design tokens instead of being written to the DOM at runtime.
 */
const userMenuDropdownMessages = defineMessages({
  avatarAlt: {
    id: 'tels.header.user.avatarAlt',
    defaultMessage: 'User avatar',
    description: 'Alt text for the user avatar image in the header user menu toggle',
  },
});

const ChevronIcon = ({ isOpen }) => (
  <svg
    aria-hidden="true"
    focusable="false"
    viewBox="0 0 512 512"
    className={`tels-user-menu-toggle-chevron${isOpen ? ' is-open' : ''}`}
  >
    <path
      fill="currentColor"
      d="M233.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 338.7 86.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"
    />
  </svg>
);

// Profile ships @edx/frontend-component-header v6, which has no
// DesktopUserMenuToggleSlot to swap in DesktopUserMenuToggleAvatar below.
// Fall back to overriding the username/avatar props on the native
// DesktopHeader/MobileHeader itself via header_desktop.v1 / header_mobile.v1
// (Modify supports mergeProps on those slots), so the full display name and
// photo still show there instead of the bare login username.
const modifyHeaderUsername = (widget) => {
  const { authenticatedUser } = useContext(AppContext);
  // eslint-disable-next-line no-param-reassign
  widget.content = {
    ...widget.content,
    username: authenticatedUser?.name || authenticatedUser?.username || null,
    avatar: authenticatedUser?.profileImage?.imageUrlFull || authenticatedUser?.avatar || null,
  };
  return widget;
};

// Desktop/mobile user-menu toggle: avatar image (or a generic account icon
// when the learner has none) + display name + chevron. Swapped in for
// org.openedx.frontend.layout.header_desktop_user_menu_toggle.v1's
// default_contents. Renders inside the header's own <Dropdown.Toggle>
// <button>, so aria-expanded is read off that ancestor rather than tracked
// locally.
const DesktopUserMenuToggleAvatar = () => {
  const intl = useIntl();
  const { authenticatedUser } = useContext(AppContext);
  const avatar = authenticatedUser?.avatar || authenticatedUser?.profileImage?.imageUrlFull;
  const displayName = authenticatedUser?.name || authenticatedUser?.username || '';
  const containerRef = useRef(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const trigger = containerRef.current?.closest('button');
    if (!trigger) {
      return undefined;
    }

    const syncOpenState = () => {
      setIsOpen(trigger.getAttribute('aria-expanded') === 'true');
    };

    syncOpenState();

    const observer = new MutationObserver(syncOpenState);
    observer.observe(trigger, { attributes: true, attributeFilter: ['aria-expanded'] });

    return () => observer.disconnect();
  }, []);

  return (
    <span ref={containerRef} className="d-inline-flex align-items-center">
      {avatar ? (
        <img
          src={avatar}
          alt={intl.formatMessage(userMenuDropdownMessages.avatarAlt)}
          className="rounded-circle mr-2 tels-user-menu-toggle-avatar"
        />
      ) : (
        <span
          className="overflow-hidden d-inline-flex rounded-circle mr-2 align-items-center justify-content-center tels-user-menu-toggle-avatar-container"
          aria-hidden="true"
        >
          <Icon src={AccountCircle} />
        </span>
      )}
      <span className="mr-2 tels-user-menu-toggle-name">
        {displayName}
      </span>
      <ChevronIcon isOpen={isOpen} />
    </span>
  );
};
