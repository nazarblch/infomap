# Global registry for instance registration
resource_registry = {}

def provides(name):
    """Class decorator for an instance provider.
    The name passed in is what the attribute is called.
    The instance will be auto registered in the registry
    with the value of the handle
    TODO : the name could also be a function which could return the
    attribute name to extract the instance name from
    """
    def wrapper(cls):
        def init_and_register(init):
            def inner(self,*args,**kwargs):
                "The new wrapper constructor"
                # Call the old constructor
                init(self,*args,**kwargs)
                # Update the resource registry with the desired key and instance
                resource_registry[self.__dict__[name]] = self
            return inner
            # Replace the constructor with a wrapped constructor
        cls.__init__ = init_and_register(cls.__init__)
        return cls
    return wrapper

def requires(*resource_types):
    """ Class decorator to inject instances from the registry
    into the instance under construction"""
    def wrap_constructor(self,*args,**kw):
        "The constructor wrapper"
        # First call the original constructor
        self.__oldinit__(*args,**kw)
        # If this instance requires dependencies to be injected
        if hasattr(self,'_resource_types') :
            # for each dependency
            for resource_type in self._resource_types:
                # inject the dependency directly as in instance variable
                # from the resource registry
                self.__dict__[resource_type] = resource_registry[kw[resource_type]]

    def inner(cls):
        cls._resource_types = resource_types
        cls.__oldinit__ = cls.__init__
        cls.__init__ = wrap_constructor
        return cls

    return inner

# The following class indicates a sample resource provider which could be
# injected. The 'handle' passed to the class decorator is the name of the attribute
# whole value will be used as the key to register the instance name in the registry
@provides('handle')
class Provider(object):
    def __init__(self,handle):
        self.handle = handle
    def __str__(self):
        return 'Provider(%s)' % self.handle

# A sample user object (ie. the object into which the dependency is to be injected
# The constructor needs to accept kw based arguments for the injection to happen
# The requires decorator lists the attribute names under which the dependencies will
# be injected into the instance of this class
@requires('first','second')
class User(object):
    def __init__(self, **kwargs):
        pass

