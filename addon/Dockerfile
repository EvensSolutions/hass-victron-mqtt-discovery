ARG BUILD_VERSION
FROM ghcr.io/evenssolutions/hass-victron-mqtt-discovery:${BUILD_VERSION} AS source

FROM ghcr.io/home-assistant/base:latest

RUN mkdir -p /app
WORKDIR /app

COPY --from=source /app/ /app/

RUN apk add --no-cache python3 && \
    python3 -m venv /app && \
    . /app/bin/activate && \
    pip install --no-cache -r requirements.txt

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
