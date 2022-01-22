
class ReturnError(Exception):
    def __init__(self, code, message=None, http_code=None):
        self.code = code
        self.message = message if message else ReturnCode.code_msg.get(code)
        self.http_code = http_code

    def __str__(self):
        return self.message

class ReturnCode:
    code_msg = {
        0: 'ok',
        1: 'internal error',
        2: 'register failed',
        3: 'user existed',
        4: 'please login',
        5: 'email or password invalid, please retry',
        6: 'login failed, please retry later',
        7: 'unauthorized',
        8: 'invalid request', # parameter error
        9: 'api key generate failed',
        10: 'key existed',
        11: 'create url failed',
    }
