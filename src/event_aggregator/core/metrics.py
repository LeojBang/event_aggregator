from prometheus_client import Counter, Gauge, Histogram

# Количество HTTP запросов
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests received",
    ["method", "endpoint", "status"],  # Метки (labels)
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
    ],  # Корзины в секундах
)

events_provider_requests_total = Counter(
    "events_provider_requests_total",
    "Total number of HTTP requests sent to the events provider API",
    ["endpoint", "status"],  # Метки (labels)
)

events_provider_request_duration_seconds = Histogram(
    "events_provider_request_duration_seconds",
    "Duration of HTTP requests to the events provider API in seconds",
    ["endpoint"],
    buckets=[
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
    ],  # Корзины в секундах
)

cache_hits_total = Counter("cache_hits_total", "Total number of cache hits")

cache_misses_total = Counter("cache_misses_total", "Total number of cache misses")

events_total = Gauge("events_total", "Current total number of events in the system")

tickets_created_total = Gauge(
    "tickets_created_total", "Current total number of tickets created"
)

tickets_cancelled_total = Gauge(
    "tickets_cancelled_total", "Current total number of tickets cancelled"
)
