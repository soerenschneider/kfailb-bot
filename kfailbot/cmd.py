import logging

import configargparse

from kfailbot import bot


def parse_args():
    """
    Returns parsed args.
    :return:
    """
    parser = configargparse.ArgumentParser(prog='k-fail-bot')

    parser.add_argument('-s', '--stream-name', dest="stream_name", action="store",
                        env_var="KFAILBOT_STREAM_NAME", default="kfailb_incidents")
    parser.add_argument('-t', '--token', action="store", env_var="KFAILBOT_TOKEN", required=True)
    parser.add_argument('--debug', action="store", env_var="KFAILBOT_DEBUG", default=False)
    parser.add_argument('-r', '--redis-host', dest="redis_host", action="store", env_var="KFAILBOT_REDIS",
                        required=True)
    parser.add_argument('--redis-port', dest="redis_port", type=int, action="store", default=6379,
                        env_var="KFAILBOT_REDIS_PORT")
    parser.add_argument('--pg-host', dest="pg_host", action="store", env_var="KFAILBOT_PG_HOST", required=True)
    parser.add_argument('--pg-user', dest="pg_user", action="store", env_var="KFAILBOT_PG_USER", required=True)
    parser.add_argument('--pg-pw', dest="pg_pw", action="store", env_var="KFAILBOT_PG_PW", required=True)
    parser.add_argument('--pg-db', dest="pg_db", action="store", env_var="KFAILBOT_PG_DB", default="kfailbot")
    parser.add_argument('--prometheus-port', type=int, dest="prometheus_port",
                        action="store", env_var="KFAILB_PROMPORT", default=8080)

    return parser.parse_args()


def setup_logging(args):
    """
    Sets up logging.
    :param args: The parsed arguments.
    :return: None
    """
    level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)
    logging.getLogger("telegram").setLevel(logging.WARNING)


if __name__ == "__main__":
    args = parse_args()
    setup_logging(args)
    kfailbot = bot.KFailBot(args)
    kfailbot.start()