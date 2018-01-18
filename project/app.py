import requests
from flask import Flask, render_template, session, redirect, request, url_for, g
from twitter_adapter import TwitterAdapter
from database import Database
from user import User

app = Flask(__name__)
app.secret_key = 'fdj32ÖÄ!?=2snkj385lasf)/#3*nal212kjfnf'  # Key for encryption of cookie data

Database.initialize(host="localhost", database="learning", user="postgres", password="POSTGRES")
twitter = TwitterAdapter()


@app.before_request
def load_user():
    if 'screen_name' in session:
        g.user = User.load_from_db_by_screen_name(session['screen_name'])


@app.route('/')
def homepage():
    return render_template('home.html')


@app.route('/login/twitter')
def twitter_login():
    if 'screen_name' in session:
        return redirect(url_for('profile'))

    request_token = twitter.get_request_token()
    session['request_token'] = request_token

    return redirect(twitter.get_qualified_authorisation_url(request_token))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))


@app.route('/auth/twitter')
def twitter_auth():
    oauth_verifier = request.args.get('oauth_verifier')
    access_token = twitter.get_access_token(session['request_token'], oauth_verifier)

    user = User.load_from_db_by_screen_name(access_token['screen_name'])
    if not user:
        user = User(access_token['screen_name'], access_token['oauth_token'],
                    access_token['oauth_token_secret'], None)
        user.save_to_db()

    session['screen_name'] = user.screen_name

    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    return render_template('profile.html', user=g.user)


def get_tweets_as_text_list_by_query(query):
    tweets = twitter.perform_request(g.user, 'https://api.twitter.com/1.1/search/tweets.json?q={}'.format(query))
    return [{'tweet': tweet['text'], 'label': 'neutral'} for tweet in tweets['statuses']]


@app.route('/search')
def search():
    if not g.user:
        return redirect(url_for('profile'))

    query = request.args.get('q')
    tweet_texts = get_tweets_as_text_list_by_query(query)

    for tweet in tweet_texts:
        r = requests.post('http://text-processing.com/api/sentiment/', data={'text': tweet['tweet']})
        json_response = r.json()
        label = json_response['label']
        tweet['label'] = label

    return render_template('search.html', tweets=tweet_texts)


app.run(port=4995, debug=True)


