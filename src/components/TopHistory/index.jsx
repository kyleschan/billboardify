import React from 'react';

import ListPage from '../ListPage';
import TopHistoryTrack from '../TopHistoryTrack';
import ListActionPanel from '../ListActionPanel';
import {Calendar} from '../Calendar/Calendar';
import ThemeColors from '../../constants/ThemeColors';
import './TopHistory.css';

const trackImg = require('../../assets/images/top-tracks.jpg');

const TopHistory = ({
  date,
  updateCurrentDate,
  topHistory,
  createTracksPlaylist
}) => (
  <div className="top-history">
    <ListPage
      headerImageSrc={trackImg}
      title={date}
      themeColor={ThemeColors.BLUE}
    >
      <div>
        <Calendar onSelection={updateCurrentDate}/>
        {topHistory
          .get('tracks')
          .map((track, index) => (
            <TopHistoryTrack
              orderNumber={index + 1}
              track={track}
              key={`${index}`}
            />
          ))}

        {topHistory.get('tracks').size > 0 && (
          <ListActionPanel
            title="Create a Playlist"
            description={`This creates a playlist from the selected week's Top 50 (if available on Spotify).`}
            onActionClick={createTracksPlaylist}
          />
        )}
      </div>
    </ListPage>
  </div>
);

export default TopHistory;
