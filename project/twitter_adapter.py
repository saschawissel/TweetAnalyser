import constants
import oauth2
import urllib.parse as urlparse
import json


class TwitterAdapter:
    def __init__(self):
        self.consumer = oauth2.Consumer(constants.CONSUMER_KEY, constants.CONSUMER_SECRET)

    def get_request_token(self):
        # Use client to perform a request to get a request token from Twitter
        client = oauth2.Client(self.consumer)
        response, content = client.request(constants.REQUEST_TOKEN_URL, 'POST')
        if response.status != 200:
            print("An error occurred getting the request token from Twitter.")

        # Twitter return the token as a URL query string. Parse that to get a dictionary of values.
        return dict(urlparse.parse_qsl(content.decode('UTF-8')))

    def get_access_token(self, request_token, verifier):
        # Create a token object with the request token and the PIN ("verifier")
        token = oauth2.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
        token.set_verifier(verifier)

        # Create a new client for the consumer (=our app) with the token (that contains the authorisation)
        client = oauth2.Client(self.consumer, token)

        # With this client aks Twitter for an access token, which we will get, because we have a verified request token
        response, content = client.request(constants.ACCESS_TOKEN_URL, 'POST')
        if response.status != 200:
            print("An error occurred getting the access token from Twitter.")

        access_token = dict(urlparse.parse_qsl(content.decode('UTF-8')))

        return access_token

    def get_qualified_authorisation_url(self, request_token):
        return "{}?oauth_token={}".format(constants.AUTHORIZATION_URL, request_token['oauth_token'])

    def perform_request(self, user, url, verb='GET'):
        authorized_token = oauth2.Token(user.oauth_token, user.oauth_token_secret)
        authorized_client = oauth2.Client(self.consumer, authorized_token)

        # Make authorized API calls
        response, content = authorized_client.request(url, verb)
        if response.status != 200:
            print("An error occurred when searching!")

        return json.loads(content.decode('utf-8'))
