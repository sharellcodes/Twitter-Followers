import twitter
from functools import partial
from sys import maxsize as maxint
import sys
import time
from urllib.error import URLError
from http.client import BadStatusLine
import networkx as nx
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

# Credentials
CONSUMER_KEY = 'b70MIYS2d9pnhnXLwIisgojPG'
CONSUMER_SECRET = 'NR0SXDQXu1q0LF0DhBEVZsDlnXuFpuX7LWwj358ccEOPcxm8RV'
OAUTH_TOKEN = '1232047548355022854-J5oFCCVxahHV2jofLUecQZwW9QZJW3'
OAUTH_TOKEN_SECRET = 'clLbPkuVYyYBoQBLi7BefIdtrcfKkPPwW46kQO3yKN7q9'
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

            print('Fetched {0} total {1} ids for {2}'.format(len(ids), label, (user_id or screen_name)), file=sys.stderr)


            if len(ids) >= limit or response is None:
                break

    return followers_ids[:followers_limit]


'''
Objective: Find the number/percentage of followers of the given users that overlap
Input: two user ids - could later be a list of ids instead
Output: Number (%) between 0 and 100
'''


##### Using User ID #####
#user1 = 18277655   #Peter King - NY - Republican
#user2 = 2970462034 #Kathleen Rice - NY - Democrat
#user3 = 22545491   #Ken Calvert - CA - Republican
#user4 = 312134473  #Linda Sanchez - CA - Democrat

    
#user1_followers = get_friends_followers_ids(twitter_api, user_id=user1, friends_limit=0, followers_limit=maxint)
#user2_followers = get_friends_followers_ids(twitter_api, user_id=user2, friends_limit=0, followers_limit=maxint)
#user3_followers = get_friends_followers_ids(twitter_api, user_id=user3, friends_limit=0, followers_limit=maxint)
#user4_followers = get_friends_followers_ids(twitter_api, user_id=user4, friends_limit=0, followers_limit=maxint)

##### Using Screen Name #####
user1 = 'RepPeteKing'      #Peter King - NY - Republican
user2 = 'RepKathleenRice'  #Kathleen Rice - NY - Democrat
user3 = 'KenCalvert'       #Ken Calvert - CA - Republican
user4 = 'RepLindaSanchez'  #Linda Sanchez - CA - Democrat

user1_followers = get_friends_followers_ids(twitter_api, screen_name=user1, friends_limit=0, followers_limit=maxint)
user2_followers = get_friends_followers_ids(twitter_api, screen_name=user2, friends_limit=0, followers_limit=maxint)
user3_followers = get_friends_followers_ids(twitter_api, screen_name=user3, friends_limit=0, followers_limit=maxint)
user4_followers = get_friends_followers_ids(twitter_api, screen_name=user4, friends_limit=0, followers_limit=maxint)

#Common Followers Between User 1 and the other users
in_common12 = len(set(user1_followers) & set(user2_followers))
in_common13 = len(set(user1_followers) & set(user3_followers))
in_common14 = len(set(user1_followers) & set(user4_followers))

#Common Followers Between User 2 and the other users
#in_common21 = len(set(user2_followers) & set(user1_followers))
in_common23 = len(set(user2_followers) & set(user3_followers))
in_common24 = len(set(user2_followers) & set(user4_followers))

#Common Followers Between User 3 and the other users
#in_common31 = len(set(user3_followers) & set(user1_followers))
#in_common32 = len(set(user3_followers) & set(user2_followers))
in_common34 = len(set(user3_followers) & set(user4_followers))

#Common Followers Between User 4 and the other users
#in_common41 = len(set(user4_followers) & set(user1_followers))
#in_common42 = len(set(user4_followers) & set(user2_followers))
#in_common43 = len(set(user4_followers) & set(user3_followers))



# % of user1's followers that also follow other users
user12_result = (in_common12/len(user1_followers)) * 100
user13_result = (in_common13/len(user1_followers)) * 100
user14_result = (in_common14/len(user1_followers)) * 100

# % of user2's followers that also follow other users
user21_result = (in_common12/len(user2_followers)) * 100
user23_result = (in_common23/len(user2_followers)) * 100
user24_result = (in_common24/len(user2_followers)) * 100

# % of user3's followers that also follow other users
user31_result = (in_common13/len(user3_followers)) * 100
user32_result = (in_common23/len(user3_followers)) * 100
user34_result = (in_common34/len(user3_followers)) * 100

# % of user4's followers that also follow other users
user41_result = (in_common14/len(user4_followers)) * 100
user42_result = (in_common24/len(user4_followers)) * 100
user43_result = (in_common34/len(user4_followers)) * 100

print('\n')
print('User 1 Followers that Follow User 2: ', user12_result)
print('\n')
print('User 1 Followers that Follow User 3: ', user13_result)
print('\n')
print('User 1 Followers that Follow User 4: ', user14_result)
print('\n')

print('User 2 Followers that Follow User 1: ', user21_result)
print('\n')
print('User 2 Followers that Follow User 3: ', user23_result)
print('\n')
print('User 2 Followers that Follow User 4: ', user24_result)
print('\n')

print('User 3 Followers that Follow User 1: ', user31_result)
print('\n')
print('User 3 Followers that Follow User 2: ', user32_result)
print('\n')
print('User 3 Followers that Follow User 4: ', user34_result)
print('\n')

print('User 4 Followers that Follow User 1: ', user41_result)
print('\n')
print('User 4 Followers that Follow User 2: ', user42_result)
print('\n')
print('User 4 Followers that Follow User 3: ', user43_result)
print('\n')


#####First Graph that compares just two people #####
#print(user1_result, user2_result)

#objects = (user1, user2)
#y_pos = np.arange(len(objects))
#performance = [user1_result, user2_result]

#plt.bar(y_pos, performance, align='center', alpha=0.5)
#plt.xticks(y_pos, objects)
#plt.ylabel('Percentage of Followers That Follow A Rival')
#plt.title('Comparing Follower Intersections')

#plt.show()


##### Fancy colored graph that compares four people #####
# data to plot
n_groups = 4
means_user1 = (0, user12_result, user13_result, user14_result)
means_user2 = (user21_result, 0, user23_result, user24_result)
means_user3 = (user31_result, user32_result, 0, user34_result)
means_user4 = (user41_result, user42_result, user43_result, 0)

# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.2
opacity = 0.8

rects1 = plt.bar(index, means_user1, bar_width,
alpha=opacity,
color='b',
label=user1)

rects2 = plt.bar(index + bar_width, means_user2, bar_width,
alpha=opacity,
color='g',
label=user2)

rects3 = plt.bar(index + bar_width + bar_width, means_user3, bar_width,
alpha=opacity,
color='y',
label=user3)

rects4 = plt.bar(index + bar_width + bar_width + bar_width, means_user4, bar_width,
alpha=opacity,
color='r',
label=user4)

plt.xlabel('Politician')
plt.ylabel('Percent of Common Followers')
plt.title('Common Twitter Followers Between Politicians')
plt.xticks(index + bar_width + bar_width, (user1, user2, user3, user4))
plt.legend()

plt.tight_layout()
plt.show()
