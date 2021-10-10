from datetime import datetime, timedelta
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import time
from typing import Any, Dict, Optional

import emails
from emails.template import JinjaTemplate
from google.api_core.exceptions import AlreadyExists
from google.cloud import pubsub_v1
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler, ContainerEngineHandler
from jose import jwt

from src.config import settings


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Get system-wide logger."""
    root_logger = logging.getLogger()

    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if settings.CONSOLE_LOGGING:
        # typically that also should be disabled when cloud logging set up
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if settings.CLOUD_LOGGING:
        # cloud handler is already present?
        if not any(
            isinstance(handler, (CloudLoggingHandler, ContainerEngineHandler))
            for handler in root_logger.handlers
        ):
            client = google.cloud.logging.Client()

            # let the client get the appropriate handler if in GKE
            client.get_default_handler()
            client.setup_logging()

    elif settings.FILE_LOGGING:
        # set only if cloud logging is disabled
        file_handler = TimedRotatingFileHandler(
            "application.log", when="D", interval=1, backupCount=2
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = get_logger(__name__)


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["email"]
    except jwt.JWTError:
        return None


def create_topic(project_id: str, topic_id: str) -> None:
    """Create pubsub topic.
    https://cloud.google.com/pubsub/docs/admin#creating_a_topic
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    try:
        topic = publisher.create_topic(request={"name": topic_path})

        logger.info("Topic created: %s", topic.name)
    except AlreadyExists:
        logger.info("Topic '%s' already exists", str(topic_path))


def create_pull_subscription(
    project_id: str, topic_id: str, subscription_id: str
) -> None:
    """Create pubsub subscription to the topic specified.
    https://cloud.google.com/pubsub/docs/admin  # creating_a_topic
    """

    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    # Wrap the subscriber in a 'with' block to automatically call close() to
    # close the underlying gRPC channel when done.
    try:
        with subscriber:
            subscription = subscriber.create_subscription(
                request={"name": subscription_path, "topic": topic_path}
            )

        logger.info("Subscription created: %s", str(subscription))
    except AlreadyExists:
        logger.info(
            "Subscription '%s' already exists for topic `%s`",
            str(subscription_path),
            str(topic_path),
        )


def publish_with_err_handler(project_id: str, topic_id: str, data: str) -> None:
    """Publish a message to the topic specified."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    futures = dict()

    def get_callback(f, data):
        def callback(f):
            try:
                logger.debug(f.result())
                futures.pop(data)
            except Exception:
                logger.error("Please handle %s for %s.", f.exception(), data)

        return callback

    futures.update({data: None})
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data.encode("utf-8"))
    futures[data] = future
    # Publish failures shall be handled in the callback function.
    future.add_done_callback(get_callback(future, data))

    # Wait for all the publish futures to resolve before exiting.
    while futures:
        time.sleep(5)

    logger.info("Published message %s with error handler to %s", data, str(topic_path))
