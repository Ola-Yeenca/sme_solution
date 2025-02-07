# API Reference

## Cache Operations
- **Cache Keys**: Format `business_name|business_type`
- **TTL**: 3600 seconds (1 hour)
- **Methods**: 
  - **get(key: str)**: Retrieves value by key
  - **set(key: str, value: Any, ttl: int)**: Stores value with time-to-live in seconds
  - **delete(key: str)**: Deletes value by key
