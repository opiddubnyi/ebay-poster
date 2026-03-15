class PosterError(Exception):
    """Base exception for poster."""


class AuthError(PosterError):
    """Authentication or authorization failure."""


class ListingError(PosterError):
    """Listing creation or publishing failure."""


class MediaError(PosterError):
    """Image upload or processing failure."""
