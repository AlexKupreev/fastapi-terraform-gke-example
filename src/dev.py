"""Dev scripts."""
import argparse
import sys

from src.config import settings
from src.utils import publish_with_err_handler


def publish_test_message() -> None:
    """Publish a message to a Pub/Sub topic with an error handler."""
    publish_with_err_handler(
        settings.PUBSUB_PROJECT_ID, settings.TOPIC_ID, "Test message"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--command", help="Command to run", required=True)

    args = parser.parse_args()

    getattr(sys.modules[__name__], args.command)()
