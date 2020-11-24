import React, { Component } from 'react';

import changeThemeColor from '../../services/change-theme';
import {toSaturday} from '../../concepts/calendar';
import './ListPage.css';

class ListPage extends Component {
  componentDidMount() {
    const { themeColor } = this.props;
    if (themeColor) {
      changeThemeColor(themeColor);
    }
  }

  render() {
    const { headerImageSrc, title, children } = this.props;

    return (
      <div className="list-page">
        <div style={{ backgroundImage: `url(${headerImageSrc})` }} className="list-page__image" />
        <h1 className="list-page__title">Billboard Top 50</h1>
        <h2 className="list-page__subtitle">Week of {toSaturday(title)}</h2>
        <div className="list-page__content">
          <div className="list-page__list">{children}</div>
        </div>
      </div>
    );
  }
}

export default ListPage;
