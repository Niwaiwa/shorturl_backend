from secrets import token_hex, token_urlsafe


class Base64Key(object):

    def gen_key(self, length: int = 6):
        return token_urlsafe(length) # or 8


if __name__ == "__main__":
    key = Base64Key().gen_key()
    print(key)
