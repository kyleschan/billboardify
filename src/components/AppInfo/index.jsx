import React, { Component } from 'react';
import { Link } from 'react-router-dom';

import config from '../../config';

import Modal from '../Modal';
import './AppInfo.css';

class AppInfo extends Component {
  render() {
    const scopes = config.SPOTIFY_AUTH_SCOPES.split(' ');
    return (
      <Modal>
        <div className="app-info">
          <h1>Billboardify App</h1>
          <p>
            This app allows users to both discover and save hits from past weeks of 
            the Billboard Top 50.
            It uses the Spotify Web API to save playlists, should you wish to do so.
          </p>
          <h3>Required Spotify access</h3>
          <p>
            Billboardify requires access to your Spotify account to save playlists. It uses the Spotify Implicit Grant Flow
            for user authorization. The app is client-side only, and your Spotify data is
            not stored in any server. For more information on the login procedure, visit this {' '}
            <a href="https://developer.spotify.com/documentation/general/guides/authorization-guide/#implicit-grant-flow" target="_blank" rel="noopener noreferrer">
              guide on the authorization process.
            </a>{' '}
          </p>
          <h3>Used Scopes</h3>
          <p>
            Scopes enable the application to access specific Spotify API endpoints. The set of
            scopes that are required for you to access this app are:
            <ul className="scope-list">{scopes.map(scope => <li>{scope}</li>)}</ul>
          </p>

          <br />
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://developer.spotify.com/documentation/general/guides/authorization-guide/"
          >
            Read more about Spotify scopes
          </a>
          <div className="app-info__buttons">
            <Link className="btn btn-secondary" to="/login">
              OK, got it{' '}
              <span aria-label="OK" role="img">
                👌🏻
              </span>
            </Link>
          </div>
        </div>
      </Modal>
    );
  }
}

export default AppInfo;
