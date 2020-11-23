import React, { Component } from 'react';
import './AppHelp.css';

class Apphelp extends Component {
  render() {
    return (
      <div>
        <div className="app-help">
          <h1>Billboardify</h1>
          <p>
            With Billboardify you can discover (or rediscover) any song that appeared on the
            Billboard Top 50 in the past 40 years!
          </p>
          <p>
            Refresh your memories by exploring each week's Top 50, and create Spotify
            playlists from your favorite weeks!
          </p>
          <h3>Spotify access</h3>
          <p>
            Billboardify requires a Spotify account. Account access is client-side only and
            secured by the OAuth 2 authentication protocol, and
            your Spotify data is not stored.  For more information on the login procedure, visit this {' '}
            <a href="https://developer.spotify.com/documentation/general/guides/authorization-guide/#implicit-grant-flow" target="_blank" rel="noopener noreferrer">
              guide on the authorization process.
            </a>{' '}
          </p>
          <h3>
            Can I log out or sign in with a different account?
          </h3>
          <p>
            Sure thing, just go to{' '}
            <a href="http://accounts.spotify.com/" target="_blank" rel="noopener noreferrer">
              accounts.spotify.com
            </a>{' '}
            and press "Log Out". To sign in with a different account, open{' '}
            <a href="https://kyleschan.github.io/billboardify/login">https://kyleschan.github.io/billboardify/login</a>{' '}
            and sign in with different
            account.
          </p>
          <div className="app-help__footer">
            <a
              className="footer__link"
              href="https://github.com/kyleschan/billboardify"
              target="_blank"
              rel="noopener noreferrer"
              title="Billboardify on Github"
            >
              <i className="ion-social-github" />
            </a>
          </div>
        </div>
      </div>
    );
  }
}

export default Apphelp;
