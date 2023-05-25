# Twitter-Followers
Data mining script. College projects

## Context
With the exception of adding and removing a few comments, this code hasn't been updated since it was written in 2020.

## Objective
Find the number/percentage of followers of the given users that overlap

## How to Use
1. Download the file to your computer.
2. Open up the file in an IDE of your choice.
3. Install any of the necessary libraries that are imported in this script using `pip install`.
4. Get Twitter credentials [here](https://developer.twitter.com/en/docs/authentication/oauth-1-0a/api-key-and-secret), and replace the fields (`CONSUMER_KEY`, `CONSUMER_SECRET`, `OAUTH_TOKEN`, `OAUTH_TOKEN_SECRET`) with those credentials.
5. If you'd like, replace the current twitter users that are being used with your desired twitter users. You can identify the users with their screen name or their user ID. Modify the screen names at lines (lines), and modify the user IDs at lines 140-150.
6. Run the code. It will likely be stopped due to rate limiting and you'll have to wait 15 minutes for it to run again. This may happen more than once.
7. The output will be a bar chart to visualize the comparisons (see [common_twitter_followes.png](https://github.com/sharellcodes/Twitter-Followers/blob/main/common_twitter_followers.png)), as well as a written summary with the percentages of the overlaps (see [overlap_percentages.txt](https://github.com/sharellcodes/Twitter-Followers/blob/main/overlap_percentages.txt))
