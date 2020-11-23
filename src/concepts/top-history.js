// # Play history concept

import { fromJS } from 'immutable';
import { createSelector } from 'reselect';

import { getTop50 }  from '../services/mongodb';
import config from '../config';

// # Action Types
const FETCH_TOP_HISTORY_SUCCESS = 'history/FETCH_TOP_HISTORY_SUCCESS';

const SET_DATE = 'history/SET_DATE';

// # Selectors
export const getTopTracks = state => state.topHistory.get('tracks');
export const getDate = state => state.topHistory.get('date');

export const getTopHistory = createSelector(getTopTracks, tracks =>
  fromJS({tracks})
);

export const getTopTracksUris = createSelector(getTopTracks, tracks =>
  tracks.map(track => track.getIn(['track_info', 'uri']))
);

const getFirstTrackImage = target => target.getIn(['track_info', 'album', 'images', 0, 'url']);

export const getTrackImages = createSelector(getTopTracks, tracks =>
  tracks.map(getFirstTrackImage)
);

// # Action Creators
export const fetchTop = () => (dispatch, getState) => {
  const date = getDate(getState());
  getTop50(date, config.REALM_KEY).then((value) =>
  dispatch(
    {type: FETCH_TOP_HISTORY_SUCCESS,
     payload: value
    }
  ));
};

export const fetchTopHistory = () => dispatch => dispatch(fetchTop());

export const setDate = date => ( 
  {type: SET_DATE,
   payload: date,
  });

// # Reducer
const initialState = fromJS({
  tracks: {},
  date: '2020-11-18',
  isLoading: false,
});

export default function reducer(state = initialState, action) {
  switch (action.type) {
    case FETCH_TOP_HISTORY_SUCCESS: {
      // Clear on fetch
      return state.set('tracks', fromJS(action.payload));
    }

    case SET_DATE: {
      console.log('The payload is', action.payload);
      return state.set('date', action.payload);
    }

    default: {
      return state;
    }
  }
}
