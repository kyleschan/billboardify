// # Play history concept

import { fromJS, Map } from 'immutable';
import { createSelector } from 'reselect';

import { getTop50 }  from '../services/mongodb';

// # Action Types
const CLEAR_TOP_50 = 'history/CLEAR_TOP_50';
const FETCH_TOP_50_SUCCESS = 'history/FETCH_TOP_50_SUCCESS';

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
  getTop50(date).then((items) => {
    dispatch({type: CLEAR_TOP_50});
    dispatch(
      {type: FETCH_TOP_50_SUCCESS,
      payload: items
      });
  });
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
    case CLEAR_TOP_50: {
      // Fill tracks
      return state.set('tracks', Map());
    }

    case FETCH_TOP_50_SUCCESS: {
      // Fill tracks
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
