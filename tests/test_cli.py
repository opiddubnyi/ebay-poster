# tests/test_cli.py
from poster.cli import build_parser, build_listing_from_args


def test_parser_post_command():
    parser = build_parser()
    args = parser.parse_args([
        "post",
        "--team", "Brazil",
        "--year", "1998",
        "--brand", "Nike",
        "--size", "XL",
        "--price", "200",
        "--photos", "front.jpg", "back.jpg",
    ])
    assert args.command == "post"
    assert args.team == "Brazil"
    assert args.price == 200.0
    assert args.photos == ["front.jpg", "back.jpg"]


def test_parser_post_with_optional_fields():
    parser = build_parser()
    args = parser.parse_args([
        "post",
        "--team", "Brazil",
        "--year", "1998",
        "--brand", "Nike",
        "--size", "XL",
        "--price", "200",
        "--photos", "front.jpg",
        "--player", "Ronaldo",
        "--type", "Home",
        "--condition", "USED_EXCELLENT",
        "--best-offer",
        "--description", "Rare jersey",
        "--custom-title", "My Title",
    ])
    assert args.player == "Ronaldo"
    assert args.type == "Home"
    assert args.condition == "USED_EXCELLENT"
    assert args.best_offer is True
    assert args.description == "Rare jersey"
    assert args.custom_title == "My Title"


def test_parser_dry_run():
    parser = build_parser()
    args = parser.parse_args([
        "post",
        "--team", "Brazil",
        "--year", "1998",
        "--brand", "Nike",
        "--size", "XL",
        "--price", "200",
        "--photos", "front.jpg",
        "--dry-run",
    ])
    assert args.dry_run is True


def test_parser_setup_command():
    parser = build_parser()
    args = parser.parse_args(["setup"])
    assert args.command == "setup"


def test_build_listing_from_args():
    parser = build_parser()
    args = parser.parse_args([
        "post",
        "--team", "Brazil",
        "--year", "1998",
        "--brand", "Nike",
        "--size", "XL",
        "--price", "200",
        "--photos", "front.jpg",
        "--type", "Home",
    ])
    listing = build_listing_from_args(args)
    assert listing.team == "Brazil"
    assert listing.price == 200.0
    assert listing.type == "Home"
    assert listing.title == "Brazil 1998 Home Football Shirt Soccer Jersey Nike size XL"
