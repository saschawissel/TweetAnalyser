from user import User
from database import Database
from twitter_adapter import TwitterAdapter


def create_new_twitter_user_in_db(email):
    access_token = get_access_token()
    user = create_user(email, access_token)
    user.save_to_db()

    return user


def get_access_token():
    request_token = twitter_adapter.get_request_token()

    # Ask the user to authorize the app via a call to Twitter with the request token und give us the PIN code
    print("Go to the following site in your browser:")
    print(twitter_adapter.get_qualified_authorisation_url(request_token))

    oauth_verifier = input("What is the PIN? ")
    return twitter_adapter.get_access_token(request_token, oauth_verifier)


def create_user(email, access_token):
    return User(email, get_firstname(), get_lastname(), access_token.key, access_token.secret, None)


def get_lastname():
    return input("Last name: ")


def get_firstname():
    return input("First name: ")


def get_email():
    return input("Email: ")


def print_tweets(tweets):
    for tweet in tweets['statuses']:
        print(tweet['text'])


# Use OAuth2 to get access to Twitter using my account and an "app" that I created on Twitter first
# (see https://apps.twitter.com/app/14653012/keys for details about this app)

Database.initialize(database="learning", user="postgres", password="POSTGRES", host="localhost")
twitter_adapter = TwitterAdapter()

user_email = get_email()
the_user = User.load_from_db_by_email(user_email)

if not the_user:
    the_user = create_new_twitter_user_in_db(user_email)

found_tweets = twitter_adapter.perform_request(the_user,
                                               'https://api.twitter.com/1.1/search/tweets.json'
                                               '?q=computers+filter:images')
print_tweets(found_tweets)
