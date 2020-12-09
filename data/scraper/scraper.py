# Python standard library imports
import datetime
import glob
import json
import os
import pickle
import re
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Third-party imports
from lxml import html
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pymongo import MongoClient


PARENTH = r'\([^)]*\)'
QUOTES = r'\"[^)]*\"'


def create_http_session(retry_strategy: Retry = None) -> requests.Session:
    """Creates an HTTP client session for web scraping.

    Args:
        retry_strategy (Retry): Retry strategy in case session is rate limited
            (429 error)

    Returns:
        requests.Session: The HTTP session equipped with retry_strategy

    """
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount ("http://", adapter)
    return session


def _get_track_info(session: requests.Session,
                    date: str = None,
                    lower_bound: int = 0,
                    upper_bound: int = 50) -> tuple:
    """Gets raw track and artist names for the given date from Billboard.

    Args:
        session (requests.Session): The HTTP session used to send GET requests
            to Billboard.
        date (str): An ISO-formatted (YYYY-MM-DD) date string. Defaults to None.
        lower_bound (int): The lower bound of the slice of the Billboard Hot 100.
            Defaults to 0.
        upper_bound (int): The upper bound of the slice of the Billboard Hot 100.
            Defaults to 50.

    Returns:
        tuple: A 2-arg tuple where the first arg is a list of the track title
            strings and the second arg is a list of the corresponding track artist
            name strings.  The ranking order is preserved.

    Raises:
        InvalidInputException: If the bounds are out of range (Must be in [0, 100]).
    """
    # Interval must be in [0, 100]
    if (lower_bound < 0 or
        upper_bound > 100 or
        lower_bound >= upper_bound):
        print('Interval must be in [0, 100]...')
        raise InvalidInputException

    chart_url = 'https://www.billboard.com/charts/hot-100/'
    page = session.get(chart_url + date)

    '''
    Uncomment code below to attempt to get Retry-After header (gives site's rate limiting policy).
    Didn't work when I tried it, however.
    '''
#     if page.status_code == 429:
#         print(page)
#         time.sleep(int(response.headers["Retry-After"]))
    
    # Make tree from page DOM
    tree = html.fromstring(page.content)
    titles_text = '//span[@class="chart-element__information__song text--truncate color--primary"]/text()'
    artists_text = '//span[@class="chart-element__information__artist text--truncate color--secondary"]/text()'
    
    # Scrape top k of Hot 100 via xpaths
    titles = tree.xpath(titles_text)[lower_bound:upper_bound]
    artists = tree.xpath(artists_text)[lower_bound:upper_bound]
    return titles, artists


def _clean_title_name(name: str) -> str:
    """Processes track title name to increase Spotify search success rate.

    Args:
        name (str): The raw track title name.

    Returns:
        str: The processed track title name.

    """
    name = name.replace("'", "") \
               .split('/', maxsplit=1)[0]
    
    # Remove parentheticals and quoted names
    name = re.sub(PARENTH, '', name)
    name = re.sub(QUOTES, '', name)
    
    # ~99% success rate currently; add more steps here if you want
    
    return name


def _clean_artist_name(name: str) -> str:
    """Processes track artist name to increase Spotify search success rate.

    Args:
        name (str): The raw track artist name.

    Returns:
        str: The processed track artist name.

    """
    name = name.replace(' Featuring', '') \
               .replace(' X ', ' ') \
               .replace(' x', '') \
               .replace(' +', '') \
               .replace(' &', '') \
               .replace("'", '') \
               .replace(".", ' ') \
               .split('/', maxsplit=1)[0] \
               .split(' With ', maxsplit=1)[0] \
               .split(' Introducing ', maxsplit=1)[0]
        
    # Remove parentheticals and quoted names
    name = re.sub(PARENTH, '', name)
    name = re.sub(QUOTES, '', name)
    
    # ~99% success rate currently; add more steps here if you want

    return name


def _get_track_uris(titles: list,
                    artists: list,
                    historical_data: dict,
                    spotify_client: spotipy.Spotify,
                    prev_week: str = None,
                    debug: bool = False,
                    record_misses_list: list = None,
                    day_of_the_week: int = 2) -> tuple:
    """Gets Spotify track URIs from track titles and artists.

    Args:
        titles (list): A list of track titles (preferably cleaned) for
            Spotify search querying.
        artists (list): A list of track artists (preferably cleaned) for
            Spotify search querying.
        historical_data: A dict with the same form as that returned by
            build_dataset.  It is used as a cache where the previous week's
            data is used if possible to prevent unnecessary expensive
            queries to Spotify.
        spotify_client (spotipy.Spotify): A Spotify client session used for
            accessing Spotify's Web API.
        prev_week (str): An ISO-formatted (YYYY-MM-DD) date string of the
            previous week. Defaults to None.
        debug (bool): If True, prints missed queries. Defaults to False.
        record_misses_list (list): A list where the query misses are
            recorded. Defaults to None.
        day_of_the_week (int): Indicates the Python day of the week
            (Ex. 0 is Monday, 1 is Tuesday, ..., 6 is Sunday). Defaults
            to 2 (Wednesday).

    Returns:
        tuple: A 2-arg tuple where the first arg is a list of the search
            query strings and the second arg is a list of the
            corresponding uri strings.  The ranking order is preserved.
            An unsuccessful query will have uri = None.

    Raises:
        InvalidInputException: If historical_data is given in an invalid
            format.
    """
    # Historical data must be a valid dataset
    if len(historical_data) > 0 and not valid_dataset(historical_data):
        print('Historical data must be a valid dataset')
        raise InvalidInputException

    # Build queries
    queries = ['track:' + title + ' artist:' + artist
               for title, artist in zip(titles, artists)]
    
    # Get previous week's queries and uris
    if prev_week:
        prev_queries = {item['query']: item['uri'] for item in historical_data[prev_week]}
    
    # Search for uris via Spotify Web API
    uris = []
    for i, query in enumerate(queries):
        # Use previous week's uri
        if prev_week and query in prev_queries:
            uri = prev_queries[query]
        else:
            found_tracks = spotify_client.search(q=query, type='track')
            items = found_tracks['tracks']['items']
            # Take first (most popular) uri
            if len(items) > 0:
                uri = items[0]['uri']
            else:
                # Try the track query plus only the first part of artist query
                new_query = 'track:' + titles[i] + ' artist:'
                if len(artists[i]) > 0:
                    trunc_artist = artists[i].split()[0]
                    new_query += trunc_artist
                found_tracks = spotify.search(q=new_query, type='track')
                items = found_tracks['tracks']['items']
                if len(items) > 0:
                    uri = items[0]['uri']
                # New query is still unsuccessful...set uri to None
                else:
                    if record_misses_list is not None:
                        prev_misses = [item[-1] for item in record_misses_list]
                        if query not in prev_misses:
                            current_week = datetime.date.today()
                            current_day = current_week.weekday()
                            if current_day != day_of_the_week:
                                current_week += datetime.timedelta(days=day_of_the_week - current_day)
                            record_misses_list.append((i, current_week, query))
                    if debug:
                        print(i, new_query)
                    uri = None

        uris.append(uri)

    return queries, uris


def build_dataset(start_date: datetime.date,
                  end_date: datetime.date,
                  spotify_client: spotipy.Spotify,
                  http_session: requests.Session,
                  historical_data: dict = None,
                  refresh: bool = True,
                  debug: bool = False,
                  record_misses_list: list = None,
                  top_k: int = 50,
                  day_of_the_week: int = 2) -> dict:
    """Builds a dataset of weekly Billboard charts.

    Args:
        start_date (datetime.date): Indicates the starting week for the
            dataset (inclusive).
        start_date (datetime.date): Indicates the ending week for the
            dataset (inclusive).
        spotify_client (spotipy.Spotify): A Spotify client session used for
            accessing Spotify's Web API.
        http_session (requests.Session): The HTTP session used to send GET
            requests to Billboard.
        historical_data: A dict with the same form as that returned by
            build_dataset.  It is used as a cache where the previous week's
            data is used if possible to prevent unnecessary expensive
            queries to Spotify.  Defaults to None.
        refresh (bool): If True, indicates that historical_data should be
            updated.  Defaults to True.
        debug (bool): If True, prints missed queries and finished dates.
            Defaults to False.
        record_misses_list (list): A list where the query misses are
            recorded. Defaults to None.
        top_k (int): Each week in the dataset will have the top_k of the
            Billboard Hot 100. Defaults to 50.
        day_of_the_week (int): Indicates the Python day of the week
            (Ex. 0 is Monday, 1 is Tuesday, ..., 6 is Sunday). Defaults
            to 2 (Wednesday).

    Returns:
        dict: Keys are ISO dates (YYYY-MM-DD) indicating the week of the
            chart and values are dicts of the form: {'title': title,
                                                     'artist': artist,
                                                     'query': query,
                                                     'uri': uri} .

    Raises:
        InvalidInputException: If historical_data is given in an invalid
            format, or if start_date and/or end_date are invalid.
    """
    dataset = historical_data if historical_data is not None else {}
    # Historical data must be a valid dataset
    if len(dataset) > 0 and not valid_dataset(dataset):
        print('Historical data must be a valid dataset')
        raise InvalidInputException

    # Convert dates to datetime.date objects
    try:
        if not isinstance(start_date, datetime.date):
            start_date = datetime.date.fromisoformat(start_date)
        if not isinstance(end_date, datetime.date):
            end_date = datetime.date.fromisoformat(end_date)
    except ValueError:
        print('Invalid start or end dates')
        raise InvalidInputException

    # Either extend or refresh the historical data
    if len(dataset) > 0:
        index = 0 if refresh else -1
        first_week = datetime.date.fromisoformat(list(dataset)[index])
        if refresh and first_week < start_date:
            start_date = first_week
    
    # Verify that dates are valid and restrict them to reasonable values
    if (start_date > end_date):
        print("Start date must be on or before end date...")
        raise InvalidInputException
    if (start_date < datetime.date(1960, 1, 1)):
        start_date = datetime.date(1960, 1, 1)
    if (end_date > datetime.date.today()):
        end_date = datetime.date.today()
    
    # Center weeks on provided day of the week
    if day_of_the_week:
        if end_date.weekday() != day_of_the_week:
            end_date += datetime.timedelta(days=day_of_the_week - end_date.weekday())
        if start_date.weekday() != day_of_the_week:
            start_date += datetime.timedelta(days=day_of_the_week - start_date.weekday())
    
    # Find all dates b/w start and end
    week = datetime.timedelta(weeks=1)
    dates = [str(start_date)]
    while start_date <= end_date:
        start_date += week
        if start_date > end_date:
            break
        dates.append(str(start_date))

    # Build the date dict and return it
    for i, date in enumerate(dates, 1):
        # If refreshing, re-use titles and artists to prevent http GET request
        if refresh and date in dataset and top_k <= len(dataset[date]):
            titles, artists = zip(*[(item['title'], item['artist']) for item in dataset[date]])
        else:
            titles, artists = _get_track_info(session=http_session,
                                              date=date,
                                              upper_bound=top_k)
        
        # Reformat title and artist strings to be compatible with Spotify API search
        clean_titles = [_clean_title_name(name) for name in titles]
        clean_artists = [_clean_artist_name(name) for name in artists]
        prev_week = str(datetime.date.fromisoformat(date) - week) if i > 1 else None
        queries, uris = _get_track_uris(clean_titles,
                                        clean_artists,
                                        dataset,
                                        spotify_client,
                                        prev_week=prev_week,
                                        debug=debug,
                                        record_misses_list=record_misses_list,
                                        day_of_the_week=day_of_the_week)
        dataset[date] = [{'title': title,
                          'artist': artist,
                          'query': query,
                          'uri': uri} 
                          for title, artist, query, uri in zip(titles, artists, queries, uris)]
        if debug:
            print(f'Finished Date {i} ({date}) of {len(dates)}')

    return dataset

def get_mongo_dataset(dataset: dict) -> list:
    """Preps a dataset of weekly Billboard charts for MongoDB upload.

    Args:
        dataset (dict): A dict with the same form as that returned by
            build_dataset.

    Returns:
        list: A list of dicts for each week in dataset. Keys of each
            dict are ISO dates (YYYY-MM-DD) indicating the week of the
            chart and values are dicts of the form: 
            {'_id': date,
             'ranking': dataset[date]}.  For MongoDB, each document is
             required to have a unique '_id' field.

    Raises:
        InvalidInputException: If dataset is given in an invalid
            format.
    """
    # Dataset must be valid
    if not valid_dataset(dataset):
        raise InvalidInputException

    # Less direct access to uris, but compatible with mongodb
    return [{'_id': date,
             'ranking': dataset[date]}
             for date
             in dataset]


def get_mongo_spotify_info(spotify_info_dict: dict) -> list:
    """Preps a dict with Spotify track info for MongoDB upload.

    Args:
        spotify_info_dict (dict): A dict with the same form as that
            returned by get_spotify_info.

    Returns:
        list: A list of dicts for each uri in spotify_info_dict.
            Keys of each dict are Spotify URIs
            (Ex. "spotify:track:0SErdEdRcVX1uJCf1eTGYH") and values
            are dicts of the form: 
            {'_id': uri,
             **spotify_info_dict[uri]}.  For MongoDB, each document is
             required to have a unique '_id' field.

    Raises:
        InvalidInputException: If spotify_info_dict is given in an
            invalid format.
    """
    # Spotify info must be valid
    if not valid_spotify_info(spotify_info_dict):
        raise InvalidInputException
    
    # Less direct access to info, but compatible with mongodb
    return [dict(_id=uri, **spotify_info_dict[uri])
            for uri in spotify_info_dict]


def save_dataset_as_json(dataset: dict,
                         path: str = os.getcwd(),
                         indent: int = None,
                         mongodb: bool = False) -> None:
    """Saves a dataset of weekly Billboard charts as a JSON file.

    Args:
        dataset (dict): A dict with the same form as that returned by
            build_dataset.
        path (str): A path string (or path-like object) indicating where
            the user would like to save the JSON file.  Defaults to
            os.getcwd(), which is the current working directory.
        indent (int): The number of spaces to indent the JSON (Ex.
            4 is typically used for JSON pretty printing). Defaults
            to None.
        mongodb (bool): If True, applies get_mongo_dataset to dataset
            before saving. Defaults to False.

    Raises:
        InvalidInputException: If dataset is given in an invalid
            format.
    """
    # Dataset must be valid
    if not valid_dataset(dataset):
        raise InvalidInputException

    # Verify existence of path
    if not os.path.exists(path):
        print(f'Given path "{path}" not found, could be a path formatting or permission error')
        return
    
    # Format file string
    file_string = 'billboard_uris_ranking'
    if mongodb: # mongodb needs to be compact
        indent = None
        file_string += '_mongodb'
    if indent:
        file_string += '_indented'
    
    
    # Record range and day of the week of data
    dates = list(dataset)
    start_date = dates[0]
    end_date = dates[-1]
    file_string += f'_{start_date}_to_{end_date}_{datetime.date.fromisoformat(start_date).strftime("%a").lower()}'

    # Version the file to prevent overwriting
    file_version = len(glob.glob(file_string + '*.json'))
    file_string += f'_v{file_version}.json'
    
    # Save dict as file_string
    with open(os.path.join(path, file_string), 'w', encoding='utf-8') as f:
        # Format dict if necessary
        save_dict = get_mongo_dataset(dataset) if mongodb else dataset
        json.dump(save_dict, f, ensure_ascii=False, indent=indent)


def save_spotify_info_as_json(spotify_info_dict: dict,
                              path: str = os.getcwd(),
                              indent: int = None,
                              mongodb: bool = False) -> None:
    """Saves a dataset of weekly Billboard charts as a JSON file.

    Args:
        spotify_info_dict (dict): A dict with the same form as that
            returned by get_spotify_info.
        path (str): A path string (or path-like object) indicating where
            the user would like to save the JSON file.  Defaults to
            os.getcwd(), which is the current working directory.
        indent (int): The number of spaces to indent the JSON (Ex.
            4 is typically used for JSON pretty printing). Defaults
            to None.
        mongodb (bool): If True, applies get_mongo_spotify_info to
            spotify_info_dict before saving. Defaults to False.

    Raises:
        InvalidInputException: If spotify_info_dict is given in an invalid
            format.
    """
    # Spotify info must be valid
    if not valid_spotify_info(spotify_info_dict):
        raise InvalidInputException

    # Verify existence of path
    if not os.path.exists(path):
        print(f'Given path "{path}" not found, could be a path formatting or permission error')
        return
    
    # Format file string
    file_string = 'billboard_uris_spotify_info'
    if mongodb: # mongodb needs to be compact
        indent = None
        file_string += '_mongodb'
    if indent:
        file_string += '_indented'
    
    # Version the file to prevent overwriting
    file_version = len(glob.glob(file_string + '*.json'))
    file_string += f'_v{file_version}.json'
    
    # Save dict as file_string
    with open(os.path.join(path, file_string), 'w', encoding='utf-8') as f:
        # Format dict if necessary
        save_dict = get_mongo_spotify_info(spotify_info_dict) if mongodb else spotify_info_dict
        json.dump(save_dict, f, ensure_ascii=False, indent=indent)
        

def manual_add_uri(dataset: dict,
                   uri: str = None,
                   query: str = None) -> None:
    """Updates dataset by adding uri to dataset at query.

    Args:
        dataset (dict): A dict with the same form as that returned by
            build_dataset.
        uri (str): Spotify URI string
            (Ex. "spotify:track:0SErdEdRcVX1uJCf1eTGYH") that the
            user would like to add to dataset.
        query (str): Spotify query string
            (Ex. "track:Rock With You artist:Michael Jackson") that
            the user would like to update with uri.

    Raises:
        InvalidInputException: If dataset is given in an invalid
            format.
    """
    # Dataset must be valid
    if not valid_dataset(dataset):
        raise InvalidInputException
    
    # Add the uri corresponding to query
    for date in dataset:
        for item in dataset[date]:
            if uri and query and item['query'] == query:
                item['uri'] = uri

                
def manual_add_uris(dataset: dict,
                    uri_dict: dict = None) -> None:
    """Updates dataset by adding all uris in uri_dict to dataset.

    Args:
        dataset (dict): A dict with the same form as that returned by
            build_dataset.
        uri_dict (dict): Dict where keys are Spotify query strings
            (Ex. "track:Rock With You artist:Michael Jackson") and
            values are Spotify URI strings
            (Ex. "spotify:track:0SErdEdRcVX1uJCf1eTGYH") that the
            user would like to add to dataset.

    Raises:
        InvalidInputException: If dataset is given in an invalid
            format.
    """
    # Dataset must be valid and uris must be in dict
    if not (valid_dataset(dataset) and isinstance(uri_dict, dict)):
        raise InvalidInputException
    
    # Add each uri in the dict to the dataset
    for query in uri_dict:
        manual_add_uri(dataset=dataset,
                       uri=uri_dict[query],
                       query=query)
        

def get_unique_uris(dataset: dict) -> set:
    """Returns the set of all unique uris in dataset.

    Args:
        dataset (dict): A dict with the same form as that returned by
            build_dataset.

    Returns:
        set: The set of all unique uris in dataset.
    Raises:
        InvalidInputException: If dataset is given in an invalid
            format.
    """
    # Dataset must be valid
    if not valid_dataset(dataset):
        raise InvalidInputException

    return {item['uri'] for date in dataset for item in dataset[date] if item['uri']}


def get_spotify_info(uris: set,
                     artist_info: bool = False,
                     audio_features: bool = False) -> dict:
    """Gets Spotify track info associated with uris.

    Args:
        uris (set): A set of uris the user would like to get Spotify
            info for.
        artist_info (bool): If True, adds Spotify artist info
            corresponding to uris. Defaults to False.
        artist_info (bool): If True, adds Spotify audio features
            corresponding to uris. Defaults to False.

    Returns: dict: Dict where keys are Spotify URI strings
            (Ex. "spotify:track:0SErdEdRcVX1uJCf1eTGYH") and values
             are dicts with requested info.  Assuming all info is
             requested, each uri corresponds to a dict of the form:
             {'track_info': spotify.track(uri)
              'audio_features': spotify.audio_features(uri)[0]
              'artist_info': spotify.artist(artist_uri)}.
            See Spotipy docs for more info:
            https://spotipy.readthedocs.io/en/2.9.0/#api-reference

    Raises:
        InvalidInputException: If any uri in uris is given in an
            invalid format.
    """
    # Verify that uris are valid
    if not valid_uris(uris):
        raise InvalidInputException

   # Build dict
    if audio_features:
        spotify_info_dict = {uri: {'track_info': spotify.track(uri),
                                   'audio_features': spotify.audio_features(uri)[0]}
                                   for uri in uris}
    else:
        spotify_info_dict = {uri: {'track_info': spotify.track(uri)}
                             for uri in uris}  
    if artist_info:
        for uri in spotify_info_dict:
            artist_uri = spotify_info_dict[uri]['track_info']['artists'][0]['uri']
            spotify_info_dict[uri]['artist_info'] = spotify.artist(artist_uri)

    return spotify_info_dict
    

def add_spotify_info_inline(dataset: dict,
                            uris: set = None,
                            spotify_info_dict: dict = None,
                            artist_info: bool = False,
                            audio_features: bool = False) -> None:
    """Updates dataset by adding Spotify info directly into dataset.
       WARNING: If storing locally, such datasets are typically quite
           large.

    Args:
        dataset (dict): A dict with the same form as that returned by
            build_dataset.
        uris (set): Set of uris that the user would like to add info
            for. If None, all unique uris in the dataset are queried
            for info. Defaults to None.
        spotify_info_dict (dict): A dict with the same form as that
            returned by get_spotify_info containing the info the user
            would like to add. If None, a dict is created from uris.
            Defaults to None.
        artist_info (bool): If True, adds Spotify artist info
            corresponding to uris. Defaults to False.
        artist_info (bool): If True, adds Spotify audio features
            corresponding to uris. Defaults to False.
    Raises:
        InvalidInputException: If dataset, spotify_info_dict, or uris
            are given in an invalid format.
    """
    # Inputs must be valid
    if not (valid_dataset(dataset) and
            valid_spotify_info(spotify_info_dict) and
            valid_uris(uris)):
        raise InvalidInputException
    
    # Get necessary parts if not provided and augment dataset
    if not uris:
        uris = get_unique_uris(dataset)
    if not spotify_info_dict:
        spotify_info_dict = get_spotify_info(uris,
                                             audio_features=audio_features,
                                             artist_info=artist_info)
    for date in dataset:
        for item in dataset[date]:
            item['spotify_info'] = spotify_info_dict[item['uri']] if item['uri'] else None
            

def valid_uris(uris: set, uri_type: str = 'track') -> bool:
    """Checks if given uris are valid.  In this case, valid means
       each uri is of the form: f"spotify:{uri_type}:{id_string}".

    Args:
        uris (set): Set of uris that the user would like to check
            for validity.
        uri_type (str): The type of uri the user would like to check
            (Ex. 'track', 'artist', 'album', etc.).
            Defaults to 'track'.

    Returns:
        bool: True if all uris are valid, else False.
    """
    # Uris must be iterable
    try:
        iterator = iter(uris)
    except TypeError:
        return False
    
    # Can't contain None type
    if None in uris:
        print(f'An element of "{uris}" has type "None", remove it and try again')
        return False
    
    # Spotify uris must be valid
    for uri in uris:
        uri_parts = uri.split(':')
        if uri_parts[0] != 'spotify' or uri_parts[1] != uri_type:
            print(f'Invalid uri {uri}')
            return False
    
    # Passed all checks; valid uri container
    return True


def valid_dataset(dataset: dict) -> bool:
    """Checks if given dataset valid.  In this case, valid means
           keys must be ISO formatted dates (YYYY-MM-DD), and each
           item in each ranking must be a dict with the following
           required keys: 'title', 'artist', 'query', 'uri'.

    Args:
        dataset (dict): A dict with the same form as that returned by
            build_dataset.

    Returns:
        bool: True if all items in the dataset are valid, else False.
    """
    # Dataset must be a dict
    if not isinstance(dataset, dict):
        return False
    
    for date in dataset:
        # Keys must be ISO formatted dates (YYYY-MM-DD)
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            print(f'Invalid date string {date}')
            return False
        # Values must be iterable
        try:
            iterator = iter(dataset[date])
        except TypeError:
            print(f'Value {dataset[date]} is not iterable')
            return False
        # Each item must be a dict with the required keys
        required_keys = {'title', 'artist', 'query', 'uri'}
        for item in dataset[date]:
            if not (isinstance(item, dict) and
                    all(key in item for key in required_keys)
            ):
                print(f'Item {item} is not a dict or does not have all required keys')
                return False

    # Passed all checks; valid dataset
    return True


def valid_spotify_info(spotify_info_dict: dict) -> bool:
    """Checks if given spotify_info_dict.  In this case, valid means
           keys must be valid Spotify track URIs
           (Ex. f"spotify:track:{id_string}"), and each
           value must be a dict with the following
           required keys: 'track_info'.

    Args:
        dataset (dict): A dict with the same form as that returned by
            build_dataset.

    Returns:
        bool: True if all items in spotify_info_dict are valid,
            else False.
    """
    # Dataset must be a dict
    if not isinstance(spotify_info_dict, dict):
        print(f'Item {spotify_info_dict} is not a dict')
        return False
    
    # Keys must be valid uris and values must be dicts with key
    # 'track_info'
    for uri in spotify_info_dict:
        uri_parts = uri.split(':')
        if uri_parts[0] != 'spotify' or uri_parts[1] != 'track':
            print(f'Invalid uri {uri}')
            return False
        
        uri_dict = spotify_info_dict[uri]
        if not isinstance(uri_dict, dict) and
           'track_info' not in uri_dict:
            print(f'Item {uri_dict} is not a valid dict')
            return False
        
    # Passed all checks; valid spotify info
    return True

def update_mongo():
    """Updates MongoDB Atlas Cluster with the latest Billboard info.
       Assumes the MongoDB database is named 'data', and there are
       *two* collections in 'data' called 'billboard_rankings' and
       'spotify_info'.  Further assumes that the MongoDB Atlas
       connection string is stored as environment variable
       ATLAS_CONNECT

    Raises:
        pymongo.errors.InvalidName: If a db or collection name is
            not found.
        pymongo.errors.DuplicateKeyError: If the function tries to
            add a document with a duplicate '_id' field to a
            collection.
        pymongo.errors.ConnectionFailure: If a connection can't be
            established with MongoDB Atlas (typically due to an
            invalid connection string).
    """
    # Get latest week's Top 50
    misses = []
    new_data = build_dataset(historical_data=None,
                             start_date=datetime.date.today(),
                             end_date=datetime.date.today(),
                             spotify_client=spotify,
                             http_session=http,
                             refresh=False,
                             debug=True,
                             record_misses_list=misses,
                             top_k=50,
                             day_of_the_week=2)

    most_recent_date = list(new_data)[-1]

    # Prep result for mongodb upload
    mongo_new_data = {'_id': most_recent_date,
                      'ranking': new_data[most_recent_date]}

    new_uris = get_unique_uris(new_data)

    # Determine which uris are new
    with open(os.path.join(os.getcwd(), '..', 'json-files', 'unique_uris.pickle'), 'rb') as f:
        uris = pickle.load(f)
    input_uris = new_uris - uris
    uris = uris | input_uris

    # Get info for those new uris and prep for mongodb upload
    new_spotify_info = get_spotify_info(input_uris,
                                        artist_info=True,
                                        audio_features=True)

    mongo_new_spotify_info = get_mongo_spotify_info(new_spotify_info)

    # Upload results to mongodb
    client = MongoClient(os.environ['ATLAS_CONNECT'])
    db = client.data
    spotify_info = db.spotify_info
    billboard_rankings = db.billboard_rankings
    if len(mongo_new_spotify_info) > 0:
        spotify_info.insert_many(mongo_new_spotify_info)
    billboard_rankings.insert_one(mongo_new_data)

    # Update and save query misses
    if len(misses) > 0:
        with open(os.path.join(os.getcwd(), '..', 'json-files', 'query_misses.pickle'), 'rb') as f:
            query_misses = pickle.load(f)
        query_misses += misses[0]
        with open(os.path.join(os.getcwd(), '..', 'json-files', 'query_misses.pickle'), 'wb') as f:
            pickle.dump(query_misses, f)
        
    with open(os.path.join(os.getcwd(), '..', 'json-files', 'unique_uris.pickle'), 'wb') as f:
        pickle.dump(uris, f)


class InvalidInputException(Exception):
    pass

if __name__ == '__main__':
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=2
    )

    http = create_http_session(retry_strategy=retry_strategy)

    update_mongo()
    # start_date = datetime.date.fromisoformat('1980-01-02')
    # end_date = datetime.date.today()
    # misses = []

    # data = build_dataset(historical_data=None,
    #                      start_date=start_date,
    #                      end_date=end_date,
    #                      spotify_client=spotify,
    #                      http_session=http,
    #                      refresh=True,
    #                      debug=True,
    #                      record_misses_list=misses,
    #                      top_k=50,
    #                      day_of_the_week=2)
    # save_dataset_as_json(data,
    #                     indent=None,
    #                     mongodb=False)
    
    # uris = get_unique_uris(data)
    # spotify_info_dict = get_spotify_info(uris=uris,
    #                                      artist_info=True,
    #                                      audio_features=True)
    # save_spotify_info_as_json(spotify_info_dict, mongodb=True)