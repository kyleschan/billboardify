// # App view concept
//
// This concept does not have reducer and it will work just as a combining
// "view-concept" for "core-concepts"

import { createStructuredSelector } from 'reselect';

import { checkLogin } from './auth';
import { fetchUserProfile, getUser } from './user';
import {
  fetchTopHistory,
  fetchTop,
  getTopHistory,
  getDate,
  setDate
} from './top-history';
import { createTopTracksPlaylist } from './playlist';
import { adjustDate, dateString } from './calendar';

// # Selectors
export const getAppViewData = createStructuredSelector({
  user: getUser,
  date: getDate,
  topHistory: getTopHistory,
});

// # Action creators
export const startAppView = () => dispatch => {
  console.log('Starting app view...');

  dispatch(checkLogin());
  dispatch(fetchUserProfile());
  dispatch(fetchTopHistory());
};

export const updateDate = (date, changeDate) => dispatch => {
  dispatch(setDate(dateString(adjustDate(date))));
  dispatch(fetchTop());
  changeDate(date);
};

export const createTracksPlaylist = createTopTracksPlaylist;
