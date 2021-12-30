from secrets import token_hex


class APIKey(object):

    def gen_api_key(self):
        return token_hex(16)


if __name__ == "__main__":
    key = APIKey().gen_api_key()
    print(key)
