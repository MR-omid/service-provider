# raise when some unexpected error happen in module
class InternalModuleError(Exception):
    @staticmethod
    def get_code():
        return 101


# raise when some of element in input are invalid or has inappropriate value
class InvalidInputError(Exception):
    @staticmethod
    def get_code():
        return 102


# use in google api module, cse not valid or expired
class WrongCseKeyError(Exception):
    @staticmethod
    def get_code():
        return 103


# use in api's module, api not valid or expired
class WrongApiKeyError(Exception):
    @staticmethod
    def get_code():
        return 104


# raise when the data is invalid
class IncorrectDataError(Exception):
    @staticmethod
    def get_code():
        return 105


# raise when need to  resolve captcha
class CaptchaNeededError(Exception):
    @staticmethod
    def get_code():
        return 106


# raise when can not access network
class NetworkError(Exception):
    @staticmethod
    def get_code():
        return 107


# raise when can not serialized an object
class SerializedError(Exception):
    @staticmethod
    def get_code():
        return 108


# raise when can not deserialized an object
class DeSerializedError(Exception):
    @staticmethod
    def get_code():
        return 109


# raise when can not access rabitmq process
class RabbitmqConnectionError(Exception):
    @staticmethod
    def get_code():
        return 110


# raise when user submit cancel request
class CancelExecutionError(Exception):
    @staticmethod
    def get_code():
        return 111


# raise when can not access database or table
class DatabaseError(Exception):
    @staticmethod
    def get_code():
        return 112


# raise when can not login on facebook
class LoginError(Exception):
    @staticmethod
    def get_code():
        return 113


# raise when can not find result in search functions
class ResultNotFoundError(Exception):
    @staticmethod
    def get_code():
        return 114


# raise when API HAS NOT CREDIT
class InsufficientCredit(Exception):
    @staticmethod
    def get_code():
        return 115


# raise when API HAS NOT CREDIT
class TwitterApiConstraint(Exception):
    @staticmethod
    def get_code():
        return 116


# raise when API HAS NOT CREDIT
class InstagramApiConstraint(Exception):
    @staticmethod
    def get_code():
        return 117


# raise when the request that submitted, drive system to error
class BadRequest(Exception):
    @staticmethod
    def get_code():
        return 118


# raise when the number of saved page by crawler, exceed by limit
class CrawlLimit(Exception):
    @staticmethod
    def get_code():
        return 119


# raise when the hrobot raise error
class InvalidResponseError(Exception):
    @staticmethod
    def get_code():
        return 120


# raise when the request of hrobot has been time out
class TimeoutResponseError(Exception):
    @staticmethod
    def get_code():
        return 121


# raise when module not set any result
class ResultNotSetError(Exception):
    @staticmethod
    def get_code():
        return 122


# raise when facebook account has been blocked
class FacebookAccountLocked(Exception):
    @staticmethod
    def get_code():
        return 123


# raise when facebook has been faced security question
class FacebookSecurityNeededSolved(Exception):
    @staticmethod
    def get_code():
        return 124


# raise when entered id is not valid
class InvalidUserId(Exception):
    @staticmethod
    def get_code():
        return 125
