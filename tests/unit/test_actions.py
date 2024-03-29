import argparse
import os

import mock

from cli import actions


def test_chunks_action():
    parser = argparse.ArgumentParser()
    parser.add_argument("chunks", action=actions.chunks_action(2), type=int, nargs="+")

    args = parser.parse_args(["0", "1", "2", "3", "4", "5"])
    assert args.chunks == [[0, 1], [2, 3], [4, 5]]

    with mock.patch.object(parser, "error") as mock_error:
        parser.parse_args(["0", "1", "2"])
        mock_error.assert_called_once_with('"chunks" args must be a multiple of 2')

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "chunks", action=actions.chunks_action(3), type=float, nargs="+"
    )

    args = parser.parse_args(["0", "1", "2", "3", "4", "5"])
    assert args.chunks == [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]]


def test_colour_action():
    parser = argparse.ArgumentParser()
    parser.add_argument("colour", action=actions.colour_action(), type=float, nargs="+")

    args = parser.parse_args(["0"])
    assert args.colour == [0.0, 0.0, 0.0, 1.0]

    args = parser.parse_args(["0", "0.5", "1.0"])
    assert args.colour == [0.0, 0.5, 1.0, 1.0]

    args = parser.parse_args(["0", "0.5", "1.0", "0.5"])
    assert args.colour == [0.0, 0.5, 1.0, 0.5]

    with mock.patch.object(parser, "error") as mock_error:
        parser.parse_args(["0.1", "0.5"])
        mock_error.assert_called_once_with(
            "Invalid number of arguments for colour, must be 1 (constant), "
            "3 (rgb) or 4 (rgba)"
        )

    with mock.patch.object(parser, "error") as mock_error:
        parser.parse_args(["0.1", "0.2", "0.3", "0.4", "0.5"])
        mock_error.assert_called_with(
            "Invalid number of arguments for colour, must be 1 (constant), "
            "3 (rgb) or 4 (rgba)"
        )

    with mock.patch.object(parser, "error") as mock_error:
        parser.parse_args(["2"])
        mock_error.assert_called_with("Colour values must be between 0.0 and 1.0")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "colour", action=actions.colour_action(integers=True), type=int, nargs="+"
    )

    args = parser.parse_args(["0"])
    assert args.colour == [0, 0, 0, 255]

    args = parser.parse_args(["128", "200", "255"])
    assert args.colour == [128, 200, 255, 255]


def test_filepath_action():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", action=actions.filepath_action())

    args = parser.parse_args(["."])
    assert args.path == os.getcwd()

    fake_dir = "/not/a/directory"
    abs_fake_dir = os.path.abspath("/not/a/directory")

    args = parser.parse_args([fake_dir])
    assert args.path == abs_fake_dir

    parser = argparse.ArgumentParser()
    parser.add_argument("path", action=actions.filepath_action(exists=True))
    with mock.patch.object(parser, "error") as mock_error:
        parser.parse_args([fake_dir])
        mock_error.assert_called_once_with(
            "Filepath does not exist: {}".format(abs_fake_dir)
        )


def test_multi_subparse_action():
    subparser = argparse.ArgumentParser()
    subparser.add_argument("--one", type=int)
    subparser.add_argument("--two", type=int)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--subparsers",
        action=actions.multi_subparse_action({"--SUB": subparser}),
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args(
        [
            "--subparsers",
            "--SUB",
            "--one",
            "1",
            "--two",
            "2",
            "--SUB",
            "--one",
            "3",
            "--two",
            "4",
        ]
    )
    assert len(args.subparsers) == 2
    assert args.subparsers == [
        {"one": 1, "two": 2, "subcommand": "--SUB"},
        {"one": 3, "two": 4, "subcommand": "--SUB"},
    ]

    # Providing additional_args for each subparser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--subparsers",
        action=actions.multi_subparse_action(
            {"--SUB": subparser}, additional_args={"--SUB": ["--two", "5"]}
        ),
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args(
        ["--subparsers", "--SUB", "--one", "1", "--SUB", "--one", "3"]
    )
    assert len(args.subparsers) == 2
    assert args.subparsers == [
        {"one": 1, "two": 5, "subcommand": "--SUB"},
        {"one": 3, "two": 5, "subcommand": "--SUB"},
    ]
