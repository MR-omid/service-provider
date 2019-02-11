import zlib
from subprocess import check_output, CalledProcessError
import datetime
import json
import logging
from colorlog import ColoredFormatter
try:
    from components.mode import debug_mode
except ImportError:
    debug_mode = True


def json_fallback(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, (bytes,bytearray)):
        return obj.decode()
    else:
        return None  # FIXME: handle other object unserializable


def to_json(data):
    return json.dumps(data, default=json_fallback, ensure_ascii=False)


def find_pid(process_name):
    try:
        return list(map(int, check_output(['pgrep', '-f', process_name]).split()))
    except CalledProcessError:
        return []


def get_rsa():
    return b"-----BEGIN RSA PRIVATE KEY-----\n\
            MIICWwIBAAKBgQCEKIftqIFKBE+haHu9UiG3b9eVlU5YhRkOVl8d6cfKx9njTW+l\n\
            obgs390mNFvdYm4x/WckKSsZN84i6S48pCirnDmDS0aPvPbIL2ueZ3d4Pm06ptox\n\
            xNrGtPehD1oMbv+znzlvdlth7lWy36f+KBzfx+7HZD9L9O4Y151nAGdE6QIDAQAB\n\
            AoGAHTKTLVdwEPk42pEp3V7a4hsMhxiwcXAeZAODCinPISbcJZLDGtXKyec/haRF\n\
            s3h+nf69HckWo4CnwyC/PViLP2M6BRBbogG3yuiyAwyu935d64LWaR6UVBKLPHCl\n\
            PPqnJoHwm0qVcT86o1qhOiF7PZ7thnVC6yOGRspV1AqWyr0CQQDpCQyf3HLZoGqL\n\
            3HlyydxSHSpbmH8JRmlANw/5xosLDMBr+k7ZqCdJfKIQqqMs8axE52F+VdkqAODH\n\
            vF0NtkZrAkEAkS6VkaQrigkJYaEBpxOx2+pUomycNSUJDN9HTfK9oXnQ7uiKYArF\n\
            BP9+TQaSQaNFA0heOnjwQ+0yHEev0lsu+wJAFGKjRRS+w0TiLSvzP9RivpgojWyw\n\
            qDoNmP14G0x/+055QrjZzvaDwUzyzGxw68yUWk63W5rc7Wy4PSDALyPj0wJAeGJf\n\
            Zbfy3m/l1o2SeD8tgUSKz3AuCyddnM3cK3d35NjE9gXfEAp+GkndKfOj/UdsJ2+v\n\
            qt6zpC+gGLEcytoPVwJAD+MhnkHAYT1e82jGlxx9kkDlyL96nhsgzkhG3iz7YthM\n\
            YTm9pDIeUImPLJ/yx8pj84uEqi4i9HC5ISs2/QkrAQ==\n\
            -----END RSA PRIVATE KEY-----"


def decrypt_rsa(message, private_key):
    """
    param: public_key_loc Path to your private key
    param: package String to be decrypted
    return decrypted string
    """
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from base64 import b64decode
    rsa_key = PKCS1_OAEP.new(RSA.importKey(private_key))
    decrypted = rsa_key.decrypt(b64decode(message))
    return decrypted


def gzip_compress(data):
    z = zlib.compressobj(-1, zlib.DEFLATED, 31)
    compress_data = z.compress(data) + z.flush()
    return compress_data


def gzip_decompress(data):
    z = zlib.decompressobj(16 + zlib.MAX_WBITS)
    decompress_data = z.decompress(data)
    return decompress_data

# use ApiLogging to print log info
class ApiLogging(object):
    log_level = logging.DEBUG
    log_format = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
    logging.root.setLevel(log_level)
    formatter = ColoredFormatter(log_format)
    stream = logging.StreamHandler()
    stream.setLevel(log_level)
    stream.setFormatter(formatter)
    log = logging.getLogger('pythonConfig')
    log.setLevel(log_level)
    log.addHandler(stream)

    @staticmethod
    def info(message, force=False):
        if debug_mode or force:
            ApiLogging.log.info(message)

    @staticmethod
    def error(message, force=False):
        if debug_mode or force:
            ApiLogging.log.error(message)

    @staticmethod
    def warning(message, force=False):
        if debug_mode or force:
            ApiLogging.log.warning(message)

    @staticmethod
    def critical(message, force=False):
        if debug_mode or force:
            ApiLogging.log.critical(message)


