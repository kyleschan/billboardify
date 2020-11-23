import React from 'react';

import ListItemCoverImage from '../ListItemCoverImage';
import './TopHistoryTrack.css';

const nullImg = require('../../assets/images/bb-placeholder.jpg');

const TopHistoryTrack = ({ track, orderNumber }) => ( track.getIn(['track_info', 'uri']) ?
  <a className="track-history__item" href={track.getIn(['track_info', 'uri'])}>
    <span className="order-number">{orderNumber}</span>
    <span className="track__info">
      <ListItemCoverImage src={track.getIn(['track_info', 'album', 'images', 2, 'url'])} />

      <span className="track__summary">
        <span className="artist__genres">
          {track
            .getIn(['artist_info', 'genres'])
            .slice(0, 3)
            .join(', ')}
        </span>
        <span className="track__artist">{track.getIn(['track_info', 'artists', 0, 'name'])}</span>
        <span className="track__track-name">{track.getIn(['track_info', 'name'])}</span>
      </span>
    </span>
    </a>
  :
  <a className="track-history__item" href="/#">
    <span className="order-number">{orderNumber}</span>
    <span className="track__info">
      <ListItemCoverImage src={nullImg} />

      <span className="track__summary">
        <span className="track__artist">{track.get('trackArtist')}</span>
        <span className="track__track-name">{track.get('trackName')}</span>
      </span>
    </span>
    </a>);

export default TopHistoryTrack;
