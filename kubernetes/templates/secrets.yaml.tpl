---
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Chart.Name }}
type: Opaque
stringData:
  SECRET_KEY: "app-secret-key"
  FIRST_SUPERUSER: "admin@example.com"
  FIRST_SUPERUSER_PASSWORD: "changethis"
  POSTGRES_SERVER: "127.0.0.1"
  POSTGRES_USER: "pg-user"
  POSTGRES_PASSWORD: "changethis"
  POSTGRES_DB: "database"
  SMTP_TLS: "True"
  SMTP_PORT: "587"
  SMTP_HOST: ""
  SMTP_USER: ""
  SMTP_PASSWORD: ""
  BASIC_HTTP_CREDS: "user:pass"
