import functools


def log_exceptions(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            # log the exception
            print(str(e) + 'asdddddddddddddddddd')
    return wrapper


@log_exceptions
def d():
    a= 1/1
    print(a)
if __name__ == '__main__':
    b = d()
    print(b)