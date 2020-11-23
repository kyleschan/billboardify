import React from 'react';
import { NavLink } from 'react-router-dom';

import './AppNavigation.css';

export default () => (
  <div className="App-navigation">
    <NavLink activeClassName="active" className="App-navigation__link" to="/app">
      <span className="icon ion-help" />
      <span className="navigation__label">App Info</span>
    </NavLink>
    <NavLink activeClassName="active" className="App-navigation__link" to="/top-tracks">
      <span class="icon ion-android-favorite-outline"> </span>
      <span className="navigation__label">Top 50</span>
    </NavLink>
    <NavLink activeClassName="active" className="App-navigation__link" to="/login">
      <span class="icon ion-android-exit"> </span>
      <span className="navigation__label">Log Out</span>
    </NavLink>

  </div>
);

