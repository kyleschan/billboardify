import * as Realm from "realm-web";

import config from '../config';


const appConfig = {
  id: config.REALM_APP_ID,
  timeout: 10000, // timeout in milliseconds
};
const app = new Realm.App(appConfig);


const loginAnonymous = async () => {
  var assert = require('assert');
  // Create API Key credentials
  const credentials = Realm.Credentials.anonymous();
  try {
    // Authenticate the user
    const user = await app.logIn(credentials);

    // `App.currentUser` updates to match the logged in user
    assert(user.id === app.currentUser.id)
    return user
  } catch(err) {
    console.error("Failed to log in", err);
  }
}

const getRanking = async (rankingCollection, date) => {
  try {
    const rankingQueryFilter = {_id: date};
    const rankingQueryOptions = {'projection': {_id: 0}};
    const rankingDocument = await rankingCollection.findOne(rankingQueryFilter, rankingQueryOptions);
    return rankingDocument.ranking;
  } catch(err) {
    console.error(`Failed to get ranking of ${date}`, err);
    return null;
  }
}

const getTrackInfo = async (trackInfoCollection, item) => {
  if (!item.uri) {
    return {'trackName': item.title,
            'trackArtist': item.artist,
            'track_info': {'uri': null},
            'artist_info': {'genres': 'N/A'}};
  }
  try {
  const trackInfoQueryFilter = {_id: item.uri};
  const trackInfoQueryOptions = {'projection': {_id: 0}};
  return trackInfoCollection.findOne(trackInfoQueryFilter, trackInfoQueryOptions);
  } catch(err) {
    console.error(`Failed to get track info of ${item.uri}`, err);
    return null;
  }
}


export const getTop50 = async (date) => {
  try {
    const user = await loginAnonymous();
    console.log("Successfully logged in!")
    const mongo = user.mongoClient("mongodb-atlas");
    const rankingCollection = mongo.db("data").collection("billboard_rankings");
    const trackInfoCollection = mongo.db("data").collection("spotify_info");
    const ranking = await getRanking(rankingCollection, date);
    const trackInfo = await Promise.all(ranking.map(item => getTrackInfo(trackInfoCollection, item)));
    return trackInfo;
  } catch(err) {
    console.error(`Failed to get Top 50 of ${date}`, err);
  }
}

