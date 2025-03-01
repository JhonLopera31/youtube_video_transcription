from argparse import ArgumentParser


def create_parser():
    parser = ArgumentParser()

    parser.add_argument(
        "--video_id",
        dest="video_id",
        help="id of the youtube video",
        type=str,
        required=True,
    )

    return parser
