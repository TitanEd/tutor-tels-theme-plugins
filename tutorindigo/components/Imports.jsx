import React, { useContext, useEffect, useRef, useState } from 'react';
import Cookies from 'universal-cookie';
import { NavLink, useLocation } from 'react-router-dom';

import { getConfig } from '@edx/frontend-platform';
import { AppContext } from '@edx/frontend-platform/react';
import { Icon } from '@openedx/paragon';
import { AccountCircle, Nightlight, WbSunny } from '@openedx/paragon/icons';
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
} from '@fortawesome/free-solid-svg-icons';
