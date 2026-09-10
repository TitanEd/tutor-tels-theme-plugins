import React, {
  useContext, useEffect, useRef, useState,
} from 'react';
import Cookies from 'universal-cookie';
import { NavLink, useLocation } from 'react-router-dom';

import { getConfig } from '@edx/frontend-platform';
import { AppContext } from '@edx/frontend-platform/react';
import { Icon } from '@openedx/paragon';
import { Nightlight, WbSunny } from '@openedx/paragon/icons';
import { defineMessages, useIntl } from '@edx/frontend-platform/i18n';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faBars,
  faTimes,
  faChevronDown,
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
