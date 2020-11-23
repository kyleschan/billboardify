import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Route, Redirect } from 'react-router-dom';

import {
  startAppView,
  createTracksPlaylist,
  getAppViewData,
  updateDate
} from '../../concepts/app-view';
import PlaylistPopup from '../PlaylistPopup';
import TopHistory from '../../components/TopHistory';
import ScrollTopRoute from '../../components/ScrollTopRoute';
import AppNavigation from '../../components/AppNavigation';
import AppHelp from '../../components/AppHelp';

import './AppView.css';

const trackImg = require('../../assets/images/top-tracks.jpg');

class AppView extends Component {
  componentDidMount() {
    this.props.startAppView();
  }

  render() {
    const {
      topHistory,
      date,
      createTracksPlaylist,
      updateDate,
      match,
    } = this.props;

    return (
      <div className="App">
        <div className="App-container">
          <AppNavigation />

          <PlaylistPopup />

          <div className="App-content">
            <Route exact path={`${match.url}`} render={() => <Redirect to="/top-tracks" />} />
            <ScrollTopRoute
              exact
              path={`${match.url}top-tracks`}
              render={() => (
                <TopHistory
                  date={date}
                  updateCurrentDate={updateDate}
                  topHistory={topHistory}
                  createTracksPlaylist={createTracksPlaylist}
                />
              )}
            />
            <ScrollTopRoute exact path={`${match.url}app`} component={AppHelp} />
          </div>
        </div>

        <div className="preload-images">
          <img key={trackImg} alt="preloaded img" src={trackImg} />
        </div>
      </div>
    );
  }
}

const mapStateToProps = getAppViewData;
const mapDispatchToProps = {
  startAppView,
  createTracksPlaylist,
  updateDate
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(AppView);
