"""
OpenTelemetry tracing with Jaeger exporter.
Provides distributed tracing across services.
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import Status, StatusCode
import uuid


def setup_tracing(app, service_name="books-api"):
    """
    Setup OpenTelemetry tracing with Jaeger exporter.
    
    Jaeger UI: http://localhost:16686
    """
    # Create resource with service name
    resource = Resource.create({"service.name": service_name})
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,  # Jaeger agent UDP port
    )
    
    # Add span processor
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Auto-instrument Flask
    FlaskInstrumentor().instrument_app(app)
    
    # Auto-instrument requests library (for auth server calls)
    RequestsInstrumentor().instrument()
    
    return trace.get_tracer(service_name)


def get_tracer():
    """Get the current tracer"""
    return trace.get_tracer("books-api")


def generate_trace_id():
    """Generate a trace ID for request correlation"""
    return str(uuid.uuid4())


def add_span_attributes(span, **attributes):
    """Add custom attributes to a span"""
    for key, value in attributes.items():
        span.set_attribute(key, str(value))


def record_exception(span, exception):
    """Record an exception in the current span"""
    span.set_status(Status(StatusCode.ERROR, str(exception)))
    span.record_exception(exception)
