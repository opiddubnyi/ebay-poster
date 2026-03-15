from poster.exceptions import PosterError, AuthError, ListingError, MediaError


def test_poster_error_is_base():
    assert issubclass(AuthError, PosterError)
    assert issubclass(ListingError, PosterError)
    assert issubclass(MediaError, PosterError)


def test_error_messages():
    err = AuthError("Token expired")
    assert str(err) == "Token expired"
    assert isinstance(err, PosterError)
