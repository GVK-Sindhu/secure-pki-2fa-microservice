# ------------------------------
# Stage 1 – Builder
# ------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies separately for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --prefix /install


# ------------------------------
# Stage 2 – Runtime
# ------------------------------
FROM python:3.11-slim AS runtime

ENV TZ=UTC
WORKDIR /app

# Install cron + timezone data
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set timezone to UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

# Copy installed Python libs
COPY --from=builder /install /usr/local



# Copy application source code
COPY src/ /app/src/
COPY scripts/ /app/scripts/
COPY cron/ /app/cron/
COPY entrypoint.sh /app/entrypoint.sh
# Copy key files required for decryption
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem
COPY encrypted_seed.txt /app/encrypted_seed.txt
COPY sign_commit.py /app/sign_commit.py


# Create persistent volume directories
RUN mkdir -p /data && mkdir -p /cron

# Permissions
RUN chmod +x /app/entrypoint.sh && \
    chmod 0644 /app/cron/2fa-cron && \
    crontab /app/cron/2fa-cron

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
