import ENV from '../env';


const config = {
  API_URL: 'https://api.spotify.com/v1',
  REALM_APP_ID: 'playlist-app-ectuj',
  SPOTIFY_AUTHORIZE_URL: 'https://accounts.spotify.com/authorize',
  SPOTIFY_AUTH_SCOPES: 'playlist-modify-public',
  SPOTIFY_CLIENT_ID: ENV.SPOTIFY_CLIENT_ID,
  CALLBACK_URL: `${window.location.origin}/billboardify/callback`,
};
export default config;
