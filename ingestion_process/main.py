import logging

from modules.ingestion_process import run_process
from utils import arg_parser
from configs.configs import LOGGER_FORMAT

def main(args):
    run_process(args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
    args = arg_parser.create_parser().parse_args()
    main(args)
