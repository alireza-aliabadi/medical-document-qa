"""OpenTelemetry instrumentation setup."""

import logging
from typing import TYPE_CHECKING

from backend.core.config import Settings

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


def setup_telemetry(settings: Settings) -> None:
    if not settings.otel_enabled:
        logger.info("OpenTelemetry disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": settings.otel_service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        # FastAPI instrumentation is applied in main after app creation
        FastAPIInstrumentor  # noqa: B018 — referenced for lazy import side-effect documentation
        logger.info("OpenTelemetry configured for %s", settings.otel_service_name)
    except ImportError:
        logger.warning("OpenTelemetry packages not available")


def instrument_fastapi(app: "FastAPI", settings: Settings) -> None:
    if not settings.otel_enabled:
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
    except ImportError:
        pass
