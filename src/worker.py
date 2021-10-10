#!/usr/bin/python3

"""Project Pub/Sub listener.
Setting up as systemd service:
https://tecadmin.net/setup-autorun-python-script-using-systemd/

Core functionality taken from https://cloud.google.com/pubsub/docs/pull
"""
import time
from concurrent.futures import TimeoutError  # pylint: disable=redefined-builtin

from google.cloud import pubsub_v1

from src import backend_pre_start
from src.config import settings
from src.utils import create_topic, create_pull_subscription, get_logger


logger = get_logger(__name__)


def init_pubsub(project_id: str, topic_id: str, subscription_id: str):
    """Create topic and subscription (for local dev)"""
    if settings.PUBSUB_AUTOCREATE_TOPIC:
        create_topic(project_id, topic_id)

    if settings.PUBSUB_AUTOCREATE_SUBSCRIPTION:
        create_pull_subscription(project_id, topic_id, subscription_id)


def callback(message):
    """Simplest callback for a pubsub message"""
    # simply write to the log
    logger.info("Received message: '%s'", str(message))
    message.ack()


backend_pre_start.main()

init_pubsub(
    settings.PUBSUB_PROJECT_ID,
    settings.TOPIC_ID,
    settings.SUBSCRIPTION_ID,
)

subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = subscriber.subscription_path(
    settings.PUBSUB_PROJECT_ID, settings.SUBSCRIPTION_ID
)

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
logger.info("Listening for messages on %s..\n", str(subscription_path))

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        time.sleep(5)
        while True:
            streaming_pull_future.result()

    except TimeoutError:
        streaming_pull_future.cancel()
