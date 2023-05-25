import twitter
from functools import partial
from sys import maxsize as maxint
import sys
import time
from urllib.error import URLError
from http.client import BadStatusLine
import networkx as nx

# Credentials
# 05/25/23 - I added 'xxx' because these credentials are user specific
CONSUMER_KEY = 'xxx'
CONSUMER_SECRET = 'xxx'
OAUTH_TOKEN = 'xxx'
OAUTH_TOKEN_SECRET = 'xxx'
auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth)


def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600:  # Seconds
            print('Too many retries. Quitting.', file=sys.stderr)
            raise e

        # See https://developer.twitter.com/en/docs/basics/response-codes
        # for common codes

        if e.e.code == 401:
            print('Encountered 401 Error (Not Authorized)', file=sys.stderr)
            return None
        elif e.e.code == 404:
            print('Encountered 404 Error (Not Found)', file=sys.stderr)
            return None
        elif e.e.code == 429:
            print('Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
            if sleep_when_rate_limited:
                print("Retrying in 15 minutes...ZzZ...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60 * 15 + 5)
                print('...ZzZ...Awake now and trying again.', file=sys.stderr)
                return 2
            else:
                raise e  # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print('Encountered {0} Error. Retrying in {1} seconds' \
                  .format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError as e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("URLError encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise
        except BadStatusLine as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("BadStatusLine encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise


def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None), \
        "Must have screen_name or user_id, but not both"

    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids, count=5000)

    friends_ids, followers_ids = [], []

    for twitter_api_func, limit, ids, label in [
        [get_followers_ids, followers_limit, followers_ids, "followers"]
    ]:

        if limit == 0: continue

        cursor = -1
        while cursor != 0:

            # Use make_twitter_request via the partially bound callable...
            if screen_name:
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else:  # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']

            print('Fetched {0} total {1} ids for {2}'.format(len(ids), label, (user_id or screen_name)),
                  file=sys.stderr)

            if len(ids) >= limit or response is None:
                break

    return followers_ids[:followers_limit]


'''
Objective: Find the number/percentage of followers of the given users that overlap
Input: two user ids - could later be a list of ids instead
Output: Number (%) between 0 and 100
'''


# I modified the get_friends_followers_ids function to only return followers
# In an attempt to save API calls (?)
def followers_in_common(user1, user2):
    user1_followers = get_friends_followers_ids(twitter_api, user_id=user1, friends_limit=0, followers_limit=maxint)
    user2_followers = get_friends_followers_ids(twitter_api, user_id=user2, friends_limit=0, followers_limit=maxint)

    in_common = len(set(user1_followers) & set(user2_followers))

    # % of user1's followers that also follow user2
    user1_result = (in_common / len(user1_followers)) * 100
    # % of user2's followers that also follow user1
    user2_result = (in_common / len(user2_followers)) * 100

    return user1_result, user2_result


followers_in_common(476285257, 3070550111)
