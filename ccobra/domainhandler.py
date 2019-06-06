""" Handles domain-specific functionality such as encoding/decoding tasks.

"""

class CCobraDomainEncoder():
    """ Domain encoder class interface. Specifies the functions to be implemented by the
    domain-specific encoder instances.

    """

    def encode_task(self, task):
        raise NotImplementedError()

    def encode_response(self, response, task):
        raise NotImplementedError()
