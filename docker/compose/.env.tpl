DOMAIN=

# Backend
PROJECT_NAME=""
SECRET_KEY=changethis
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=info@example.com

USERS_OPEN_REGISTRATION=False

# fake one
SENTRY_DSN=https://public@sentry.example.com/1

# Flower
FLOWER_BASIC_AUTH=admin:changethis

# Postgres
POSTGRES_SERVER=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# Basic HTTP Auth
BASIC_HTTP_CREDS=user:pass

# if rotating file logger should be on
FILE_LOGGING=

PUBSUB_PROJECT_ID=local_dev
TOPIC_ID=topic_id
SUBSCRIPTION_ID=subscription_id

PUBSUB_AUTOCREATE_TOPIC=
PUBSUB_AUTOCREATE_SUBSCRIPTION=