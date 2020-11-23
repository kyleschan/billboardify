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
          <h2>FAQ</h2>
          <h3>
            What's the point of this app when I can just go to Billboard's website?
          </h3>
          <p>
            This app allows you to save any week's Top 50 chart as a Spotify playlist, a feature that Billboard's website doesn't have.
            In fact, as far as I can tell, this is the only app that provides such a service.
          </p>
          <h3>Why do you need access to my Spotify account?</h3>
          <p>
            Billboardify requires a Spotify account to save playlists. Account access is client-side only and
            secured by the OAuth 2 authentication protocol, and
            your Spotify data is not stored.  For more information on the login procedure, visit this {' '}
            <a href="https://developer.spotify.com/documentation/general/guides/authorization-guide/#implicit-grant-flow"
              target="_blank"
              rel="noopener noreferrer">
              guide on the authorization process.
            </a>{' '}
          </p>
          <h3>
            Billboard charts go back to 1958, why don't you have those years?  And what about the bottom 50 songs in the Hot 100?
          </h3>
          <p>
            The songs in the app are linked to Spotify via URIs (read more about Spotify URIs {' '}
            <a href="https://community.spotify.com/t5/Spotify-Answers/What-s-a-Spotify-URI/ta-p/919201"
              target="_blank"
              rel="noopener noreferrer">
              here)
            </a>, and were scraped from Billboard's website using a web scraper made in Python (see the repo below).  Although
            the scraper's post-1980 success rate was about 99%, its success rate declined sharply for years before 1980.  This is
            due to a few reasons, but the biggest reason is that a lot of the songs simply weren't on Spotify!  The web scraper's
            success rate was also poor for songs in the bottom half of the Hot 100, especially for years pre-dating the rise of music streaming services
            (roughly 2010 and before).  As it stands, many pre-2010 songs hovering near the bottom of the Top 50 have only a couple thousand plays on
            Spotify, so you can imagine what the bottom 50 are like.  Maybe in the future the website will be expanded, but it would require
            a good deal of manual searching...
          </p>
          <h3>
            Can I log out or sign in with a different account?
          </h3>
          <p>
            Sure thing, just go to{' '}
            <a href="http://accounts.spotify.com/" target="_blank" rel="noopener noreferrer">
              accounts.spotify.com
            </a>{' '}
            and click "Log Out". To sign back in with a different account, click the icon labeled "Logout" in the nav bar on the left
            (at the bottom on mobile) to log out and sign in with a different account.
          </p>
          <h3>
            Is this project open source?
          </h3>
          <p>
            Yes it is!  Clicking the GitHub logo below will take you to the repo.
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
