class CallableEntity:
    """
    Abstract base class for all callable objects in OurScheme.
    This does NOT use abc.ABC due to project restrictions.
    """
    def __call__(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__} must override __call__()")

    def __repr__(self):
        raise NotImplementedError(f"{self.__class__.__name__} must implement __repr__()")