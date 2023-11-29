def check_header(header, key_value_pair):
    """
    Check if a specific key-value pair exists in a header string.

    Args:
    - header (str): A string containing key-value pairs separated by ';'.
    - key_value_pair (str): The key-value pair to search for in the header.

    Returns:
    - bool: True if the key-value pair is present in the header, otherwise False.

    Example:
    >>> header = "responseformat=delta;readerfeatures=deletionvectors"
    >>> contains_value = check_header(header, 'responseformat=delta')
    >>> print(contains_value)
    True
    """
    pairs = header.split(";")
    for pair in pairs:
        if pair.strip() == key_value_pair:
            return True
    return False
