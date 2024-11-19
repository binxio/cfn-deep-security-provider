#!/bin/sh

if [ "$HANDLER" == "datadog-event-forwarder" ]; then
	exec /lambda-entrypoint.sh datadog_event_forwarder.handler
fi
exec /lambda-entrypoint.sh provider.handler
