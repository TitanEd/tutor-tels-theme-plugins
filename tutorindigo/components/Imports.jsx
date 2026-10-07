import React, { useContext, useEffect, useRef, useState } from 'react';
import {
  Link, NavLink, useLocation, useNavigate,
} from 'react-router-dom';
import Cookies from 'universal-cookie';

import { getConfig } from '@edx/frontend-platform';
import { AppContext } from '@edx/frontend-platform/react';
import {
  breakpoints, Button, Card, Icon, useMediaQuery,
} from '@openedx/paragon';
import { AccountCircle, Calendar, Nightlight, WbSunny } from '@openedx/paragon/icons';
import { defineMessages, useIntl } from '@edx/frontend-platform/i18n';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faLinkedinIn,
  faFacebookF,
  faTwitter,
  faYoutube,
  faInstagram,
} from '@fortawesome/free-brands-svg-icons';
import {
  faBars,
  faTimes,
  faChevronDown,
  // template-2 header: subject mega-menu icons
  faPalette,
  faBriefcase,
  faCode,
  faDatabase,
  faGraduationCap,
  faHeartbeat,
  faUsers,
  faSquareRootAlt,
  faLaptopCode,
  faFlask,
  faGlobe,
  faBookOpen,
} from '@fortawesome/free-solid-svg-icons';
