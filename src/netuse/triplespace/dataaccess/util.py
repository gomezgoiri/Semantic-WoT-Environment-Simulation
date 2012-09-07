def locked(f):
    def wrapped(self, *args, **kwargs):
        self._lock.acquire()
        try:
            return f(self, *args, **kwargs)
        finally:
            self._lock.release()
    wrapped.__name__ = f.__name__
    wrapped.__doc__  = f.__doc__
    return wrapped