// # Playlist concept

import { fromJS } from 'immutable';
import { get, isNil,} from 'lodash';

import { getUser } from './user';
import { getTopTracksUris, getDate } from './top-history';
import { openPlaylistPopup, setPlaylistImages } from './playlist-popup';
import { apiCall } from '../services/api';

// # Action Types
const CREATE_PLAYLIST = 'playlist/CREATE_PLAYLIST';
const CREATE_PLAYLIST_SUCCESS = 'playlist/CREATE_PLAYLIST_SUCCESS';

const GET_PLAYLIST_IMAGE = 'playlist/GET_PLAYLIST_IMAGE';

const ADD_TRACKS_TO_PLAYLIST = 'playlist/ADD_TRACKS_TO_PLAYLIST';

// # Selectors
export const getCreatingPlayListStatus = state => state.playList.get('isCreatingPlaylist');
export const getPlaylistImages = state => state.playList.get('playlistImages');

// # Action Creators
export const createPlaylist = (params = {}) => (dispatch, getState) => {
  console.log('playlist state is', getState());
  const user = getUser(getState());
  console.log('user is', user);
  const userId = user.get('id');

  if (!userId) {
    return null;
  }

  return dispatch(
    apiCall({
      type: CREATE_PLAYLIST,
      url: `/users/${userId}/playlists`,
      method: 'POST',
      data: params,
    })
  );
};

export const fetchPlaylistImages = playlistId => (dispatch, getState) => {
  const user = getUser(getState());
  const userId = user.get('id');

  if (!userId) {
    return null;
  }

  return dispatch(
    apiCall({
      type: GET_PLAYLIST_IMAGE,
      url: `/users/${userId}/playlists/${playlistId}/images`,
      method: 'GET',
    })
  );
};

export const fetchNewPlaylistImage = playlistId => dispatch =>
  dispatch(fetchPlaylistImages(playlistId)).then(action =>
    dispatch(setPlaylistImages(action.payload.data))
  );

export const addTracksToPlayList = (playlistId, tracks) => (dispatch, getState) => {
  const user = getUser(getState());
  const userId = user.get('id');

  if (!userId) {
    return null;
  }

  return dispatch(
    apiCall({
      type: ADD_TRACKS_TO_PLAYLIST,
      url: `users/${userId}/playlists/${playlistId}/tracks`,
      method: 'POST',
      data: { uris: tracks },
    })
  );
};


export const createTopTracksPlaylist = () => (dispatch, getState) => {
  const state = getState();
  const tracks = getTopTracksUris(state);
  const nonNullTracks = tracks.filter(track => track != null);
  const date = getDate(state);

  if (!nonNullTracks.size) {
    return;
  }

  return dispatch(
    createPlaylist({
      name: `Billboard Top 50 • Week of ${date}`,
    })
  ).then(response => {
    const playlist = get(response, 'payload.data');
    const playlistId = get(playlist, 'id');
    const playlistUri = get(playlist, 'uri');

    if (isNil(playlistId) || !nonNullTracks.size) {
      return null;
    }

    dispatch(addTracksToPlayList(playlistId, nonNullTracks.toJS())).then(() => {
      dispatch(openPlaylistPopup(playlistUri));
      dispatch(fetchNewPlaylistImage(playlistId));
    });
  });
};


// # Reducer
const initialState = fromJS({
  isCreatingPlaylist: false,
});

export default function reducer(state = initialState, action) {
  switch (action.type) {
    case CREATE_PLAYLIST: {
      return state.set('isCreatingPlaylist', true);
    }

    case CREATE_PLAYLIST_SUCCESS: {
      return state.set('isCreatingPlaylist', false);
    }

    default: {
      return state;
    }
  }
}
