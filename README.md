# billboardify
![](docs/billboardify_usage.gif)

This application allows users to save their favorite weeks of the Billboard Top 50 (1980-) to their Spotify account using the Spotify Web API.

[Try out Billboardify](https://kyleschan.github.io/billboardify)

## Spotify API

Billboardify uses the following parts of the Spotify Web API

- [Authorization](https://developer.spotify.com/documentation/general/guides/authorization-guide/#implicit-grant-flow)
- [Creating playlist](https://developer.spotify.com/documentation/web-api/reference/playlists/create-playlist/)
- [Adding tracks to playlist](https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/)


## MongoDB

Billboardify uses MongoDB Realm and Atlas to store Billboard Top 50 information, and uses the Anonymous authentication provider to access data.

- [MongoDB Realm](https://docs.mongodb.com/realm/)
- [MongoDB Atlas](https://docs.atlas.mongodb.com/)
- [Anonymous authentication provider](https://docs.mongodb.com/realm/authentication/anonymous/)


## Development
- `git clone https://github.com/kyleschan/billboardify.git`
- `yarn install`
- `cd billboardify`
- `yarn start`

Billboardify is built on [create-react-app](https://github.com/facebook/create-react-app)

## Photo Credits

**Concert**
Photo by [Aditya Chinchure](https://unsplash.com/photos/ZhQCZjr9fHo) on [Unsplash](https://unsplash.com/)


## License
MIT
Thanks to [Replayify](https://github.com/palampinen/replayify/tree/master/src) for their styling!
