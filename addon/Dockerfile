ARG BUILD_VERSION
ARG BUILD_FROM
FROM ghcr.io/jcaprano/hass-victron-mqtt-discovery:${BUILD_VERSION} AS source

FROM ${BUILD_FROM}

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
