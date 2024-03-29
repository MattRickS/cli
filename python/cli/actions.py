import argparse
import itertools
import os


def chunks_action(n):
    """
    Examples:
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument("chunks", action=chunks_action(3), type=int, nargs="+")
        >>> args = parser.parse_args("0 1 2 3 4 5".split())
        >>> args.chunks
        # [[0, 1, 2], [3, 4, 5]]

    Args:
        n (int): Number of chunks to group the arguments into

    Returns:
        argparse.Action
    """

    class ChunksAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if len(values) % n != 0:
                parser.error('"{}" args must be a multiple of {}'.format(self.dest, n))

            array = [values[i : i + n] for i in range(0, len(values), n)]
            setattr(args, self.dest, array)

    return ChunksAction


def colour_action(alpha=True, integers=False):
    """
    Action which generates a 3 (rgb) or 4 (rgba) index list representing a colour.
    This action requires type to be set to float or int and nargs to be "+"

    Examples:
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument("colour", action=colour_action(), type=float, nargs="+")
        >>> args = parser.parse_args("0")
        >>> args.colour
        # [0.0, 0.0, 0.0, 1.0]
        >>> args = parser.parse_args("0.1 0.2 0.3".split())
        >>> args.colour
        # [0.1, 0.2, 0.3, 1.0]

    Args:
        alpha (bool): Whether or not to include an alpha value, ie, it returns a
            3 or 4 index list
        integers (bool): If True, colours are interpreted using 0-255 integer
            values instead of 0.0-1.0 floats

    Returns:
        argparse.Action
    """
    min_, max_ = (0, 255) if integers else (0.0, 1.0)

    class ColourAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if len(values) == 1:
                values *= 3
                values.append(max_)
            elif len(values) == 3:
                values.append(max_)
            elif alpha and len(values) != 4:
                parser.error(
                    "Invalid number of arguments for {}, must be 1 (constant), "
                    "3 (rgb) or 4 (rgba)".format(self.dest)
                )
            elif not alpha:
                parser.error(
                    "Invalid number of arguments for {}, must be 1 (constant) "
                    "or 3 (rgb)".format(self.dest)
                )

            if not all(min_ <= v <= max_ for v in values):
                parser.error(
                    "Colour values must be between {} and {}".format(min_, max_)
                )

            setattr(args, self.dest, values)

    return ColourAction


def filepath_action(exists=False):
    """
    Action which ensures the filepath is absolute

    Usage:
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument("path", action=filepath_action())
        >>> args = parser.parse_args(".")
        >>> args.path
        # /current/directory

    Keyword Args:
        exists (bool): If True, parser will error if the filepath does not exist

    Returns:
        argparse.Action
    """

    class FilepathAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            values = os.path.abspath(values)

            if exists and not os.path.exists(values):
                parser.error("Filepath does not exist: {}".format(values))

            setattr(args, self.dest, values)

    return FilepathAction


def multi_subparse_action(parser_mapping, additional_args=None):
    """
    Allows parsing multiple commands from a single list of arguments. Much like
    a regular subparser, it's a requirement for the argument to use
    nargs=argparse.REMAINDER. Unlike subparser, subcommands must be provided to
    the initial subparser argument for anything to be processed.

    Multiple subcommands can be provided mapped to the parser to use on each
    argument list.

    Parsed results are stored as a list of dictionaries, each dictionary
    containing the parsed keys and an additional key "subcommand" mapped to the
    name of the subcommand used parsed. The order of the dictionaries matches
    the order the arguments were provided in.

    Examples:
        >>> subparser = argparse.ArgumentParser()
        >>> subparser.add_argument("value", type=int, nargs=argparse.REMAINDER)
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument("--subparsers", action=multi_subparse_action({"--cmd": subparser}))
        >>> args = parser.parse_args(["--subparsers", "--cmd", "1", "--cmd", "2"])
        >>> args.cmd
        [{"subcommand": "cmd", "value": 1}, {"subcommand": "cmd", "value": 2}]

    Args:
        parser_mapping (dict[str, argparse.ArgumentParser]): Dictionary mapping
            command names to the ArgumentParser to use on each usage of the command
        additional_args (dict[str, list]): Dictionary mapping command names to a
            list of arguments to apply to all parsers

    Returns:
        argparse.Action
    """
    additional_args = additional_args or {}

    class MultiParseAction(argparse.Action):
        KEY_SUBCOMMAND = "subcommand"

        def __call__(self, parser, args, values, option_string=None):

            cmd = None
            namespaces = []
            for is_separator, iter_args in itertools.groupby(
                values, key=lambda f: f in parser_mapping
            ):
                arg_list = list(iter_args)
                if is_separator:
                    cmd = arg_list[0]
                    continue
                elif cmd is None:
                    parser.error("Missing command")

                if cmd in additional_args:
                    arg_list.extend(additional_args[cmd])

                subparser = parser_mapping[cmd]
                namespace = subparser.parse_args(arg_list)
                dct = vars(namespace)
                dct[self.KEY_SUBCOMMAND] = cmd
                namespaces.append(dct)

            setattr(args, self.dest, namespaces)

    return MultiParseAction
