def normalize_pagination(page=None, per_page=None):
    """
    Normalize pagination parameters.
    
    :param page: Page number (1-indexed), defaults to 1
    :type page: int
    :param per_page: Items per page, defaults to 10, max 50
    :type per_page: int
    :return: Tuple of (page, per_page) with normalized values
    :rtype: tuple
    """
    page = max(1, page or 1)
    per_page = max(1, min(50, per_page or 10))
    return page, per_page