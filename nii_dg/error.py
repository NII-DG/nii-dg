#!/usr/bin/env python3
# coding: utf-8

class UnexpectedImplementationError(Exception):
    """\
    Error class for unexpected implementation.
    This library is intended to be added to implementations under schema directory. (e.g., amed.py)
    In addition, users can generate a RO-Crate by using this library.
    Therefore, this error is raised when the implementation is not as expected.
    """
    pass


class PropsError(Exception):
    """\
    Error class for props (checking for entity properties).
    Raised at Entity dump time.
    This validation is performed by the check_props() method (this method is called in dump()) of each subclass.
    """
    pass


class GovernanceError(Exception):
    """\
    Error class for governance (validating for data governance).
    Raised at Data Governance validation time.
    This validation is performed by the validate() method of each subclass.
    """
    pass
