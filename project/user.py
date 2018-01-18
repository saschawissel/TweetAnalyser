from database import CursorFromConnectionFromPool


class User:
    def __init__(self, screen_name, oauth_token, oauth_token_secret, id):
        self.screen_name = screen_name
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.id = id

    def __repr__(self):
        return '<User {}>'.format(self.screen_name)

    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('insert into users (screen_name, oauth_token, oauth_token_secret) '
                           'values (%s, %s, %s)',
                           (self.screen_name, self.oauth_token, self.oauth_token_secret))

    @classmethod
    def load_from_db_by_screen_name(cls, screen_name):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select id, screen_name, oauth_token, oauth_token_secret'
                           ' from users where screen_name=%s', (screen_name,))
            user_data = cursor.fetchone()
            if user_data:
                return cls(id=user_data[0], screen_name=user_data[1],
                           oauth_token=user_data[2], oauth_token_secret=user_data[3])
