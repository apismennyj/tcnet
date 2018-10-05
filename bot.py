import configparser
import random
import string

import requests

config = configparser.ConfigParser(allow_no_value=True)
config.read(['bot.ini'])

number_of_users = int(config['settings']['number_of_users'])
max_posts_per_user = int(config['settings']['max_posts_per_user'])
max_likes_per_user = int(config['settings']['max_likes_per_user'])

bot_login = config['settings']['bot_login']
bot_password = config['settings']['bot_password']
host = config['settings']['host']

emails = [email.strip() for email in config['emails']]

jwt_token = None


def retrieve_jwt_token(login, password):
    response = requests.post("{}/api-token-auth/".format(host), {"username": login, "password": password})

    if response.status_code == 200:
        data = response.json()
        return data['token']
    else:
        raise Exception('Unable to retreive authentication token')


def refresh_jwt_token(jwt_token):
    response = requests.post("{}/api-token-refresh/".format(host), {"token": jwt_token})

    if response.status_code == 200:
        data = response.json()
        return data['token']
    else:
        raise Exception('Unable to refresh authentication token')


def do_like_posts(jwt_token):
    response = requests.get("{}/users/get_most_active/?max_likes_per_user={}".format(host, max_likes_per_user),
                            headers={"Authorization": "JWT {}".format(jwt_token)})

    if response.status_code == 200:
        for user in response.json():
            print("\nProcessing user #{} ({}, has {} of {} likes)".format(user['id'], user['username'],
                                                                          user['num_likes'], max_likes_per_user))

            for i in range(0, max_likes_per_user - user['num_likes']):

                response = requests.post("{}/users/like_random_post/".format(host),
                                         data={'user_id': user['id']},
                                         headers={"Authorization": "JWT {}".format(jwt_token)})

                if response.status_code == 200:
                    result = response.json()
                    print("  Liked post #{}".format(result['status']))
                elif response.status_code == 304:
                    print('No more posts left to like')
                    exit(0)
                else:
                    raise Exception('Unable to like a post for user #{} ({})'.format(user['id'], user['username']))

            jwt_token = refresh_jwt_token(jwt_token)
    else:
        raise Exception('Unable to get users list')


def generate_data(jwt_token):
    for i in range(0, int(number_of_users)):

        print("\nCreating user #{}:".format(i + 1))

        email = random.choice(emails)
        emails.remove(email)
        username = email.split('@')[0]
        password = username

        print("   username: {}\n   password: {}\n   email: {}".format(username, password, email))

        data = {
            "username": username,
            "password": password,
            "email": email,
        }

        response = requests.post("{}/users/".format(host), data=data,
                                 headers={"Authorization": "JWT {}".format(jwt_token)})

        if response.status_code == 201:

            user = response.json()
            posts_amount = random.randint(1, max_posts_per_user)

            print("\n   Creating {} post(s):".format(posts_amount))

            for p in range(0, posts_amount):
                body = ''.join(random.choice(string.ascii_letters + string.digits + '    ') for m in
                               range(10, random.randint(30, 100)))

                print("      {}: \"{}\"".format(p + 1, body))

                data = {
                    "user": user['url'],
                    "body": body,
                }
                response = requests.post("{}/posts/".format(host), data=data,
                                         headers={"Authorization": "JWT {}".format(jwt_token)})

                if response.status_code != 201:
                    raise Exception('Unable to create a post for user {}'.format(user['username']))
        else:
            raise Exception('Unable to create user {}'.format('email'))

        jwt_token = refresh_jwt_token(jwt_token)


if __name__ == "__main__":
    jwt_token = retrieve_jwt_token(bot_login, bot_password)

    generate_data(jwt_token)
    do_like_posts(jwt_token)
