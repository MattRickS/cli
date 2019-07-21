import argparse
import itertools
import os


def chunks_action(n):
    class ChunksAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if len(values) % n != 0:
                parser.error('"{}" args must be a multiple of {}'.format(self.dest, n))

            array = [values[i : i + n] for i in range(0, len(values), n)]
            setattr(args, self.dest, array)

    return ChunksAction


def colour_action():
    class ColourAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if len(values) == 1:
                values *= 3
                values.append(1.0)
            elif len(values) == 3:
                values.append(1.0)
            elif len(values) != 4:
                parser.error(
                    "Invalid number of arguments for colour, must be 1 (constant), "
                    "3 (rgb) or 4 (rgba)"
                )

            if not all(0.0 <= v <= 1.0 for v in values):
                parser.error("Colour values must be between 0 and 1")

            setattr(args, self.dest, values)

    return ColourAction


def filepath_action(exists=False):
    class FilepathAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            values = os.path.abspath(values)

            if exists and not os.path.exists(values):
                parser.error("Filepath does not exist: {}".format(values))

            setattr(args, self.dest, values)

    return FilepathAction


def multi_parse_action(parser_mapping, additional_args=None):
    class MultiParseAction(argparse.Action):
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

                if additional_args:
                    arg_list.extend(additional_args)

                subparser = parser_mapping[cmd]
                namespace = subparser.parse_args(arg_list)
                dct = vars(namespace)
                dct["type"] = cmd
                namespaces.append(dct)

            setattr(args, self.dest, namespaces)

    return MultiParseAction
