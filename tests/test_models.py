from pathlib import Path
from poster.models import Listing


def test_listing_creation():
    listing = Listing(
        team="Brazil",
        year="1998",
        brand="Nike",
        size="XL",
        price=200.0,
        photos=[Path("front.jpg")],
    )
    assert listing.team == "Brazil"
    assert listing.condition == "USED_GOOD"  # default


def test_generate_title_full():
    listing = Listing(
        team="Brazil",
        year="1998 1999 2000",
        type="Home",
        brand="Nike",
        size="XL",
        price=200.0,
        photos=[Path("front.jpg")],
    )
    title = listing.generate_title()
    assert title == "Brazil 1998 1999 2000 Home Football Shirt Soccer Jersey Nike size XL"


def test_generate_title_with_player():
    listing = Listing(
        team="Brazil",
        year="1998",
        player="Ronaldo",
        brand="Nike",
        size="L",
        price=150.0,
        photos=[Path("front.jpg")],
    )
    title = listing.generate_title()
    assert "Ronaldo" in title
    assert "Brazil" in title


def test_generate_title_minimal():
    listing = Listing(
        team="Brazil",
        year="1998",
        brand="Nike",
        size="XL",
        price=200.0,
        photos=[Path("front.jpg")],
    )
    title = listing.generate_title()
    assert "Brazil" in title
    assert "1998" in title
    assert "Nike" in title
    assert "XL" in title
    assert "Home" not in title  # no type provided


def test_custom_title_overrides():
    listing = Listing(
        team="Brazil",
        year="1998",
        brand="Nike",
        size="XL",
        price=200.0,
        photos=[Path("front.jpg")],
        custom_title="My Custom Title",
    )
    assert listing.title == "My Custom Title"


def test_title_property_auto_generates():
    listing = Listing(
        team="Brazil",
        year="1998",
        brand="Nike",
        size="XL",
        price=200.0,
        photos=[Path("front.jpg")],
    )
    assert listing.title == listing.generate_title()


def test_listing_defaults():
    listing = Listing(
        team="Brazil",
        year="1998",
        brand="Nike",
        size="XL",
        price=200.0,
        photos=[Path("front.jpg")],
    )
    assert listing.condition == "USED_GOOD"
    assert listing.best_offer is True
    assert listing.player is None
    assert listing.type is None
    assert listing.description is None
    assert listing.custom_title is None
