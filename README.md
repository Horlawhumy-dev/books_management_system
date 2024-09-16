# Books Management System

This project implements a library management system with two main components:
1. Admin API
2. Frontend API

Both services use RabbitMQ for seamless communication, allowing real-time updates between systems.

## Features

- User enrollment and management
- Book catalog browsing and filtering
- Book borrowing functionality
- Admin operations for managing books and users

## Setup and Usage

1. Clone the repository
2. Navigate to the project directory
3. Run `docker-compose up --build` to start both services
4. Access the Admin API at `http://localhost:8080/api/v1/doc/`
5. Access the Frontend API at `http://localhost:8000/api/v1/doc/`

## Documentation

API documentation is generated using Swagger and can be accessed at:
- Admin API: `http://localhost:8080/api/v1/doc/`
- Frontend API: `http://localhost:8000/api/v1/doc/`

## Testing

Unit tests are included for both services. To run tests:

1. Ensure Docker services are up
2. Navigate to the service directory (e.g., `cd admin_api`)
3. Run `docker-compose exec <service_name> pytest -vv`

## Scaling and Authentication

To scale the infrastructure for increased traffic:
- Implement auto-scaling groups for both API services
- Use load balancers to distribute traffic
- Consider implementing caching mechanisms like Redis

To handle a shared authentication scheme:
- Implement JWT for token-based authentication
- Use a centralized authentication service (e.g., OAuth2 provider)
- Securely store user credentials in a dedicated database
- Use HTTPS/TLS encryption for all API communications

## Docker Compose

The `docker-compose.yml` file in the root directory manages both services. Each service runs on a different port:
- Admin API: Port 8080
- Frontend API: Port 8000

## Prerequisites

- Python 3.8+
- Docker
- Docker Compose
- RabbitMQ
- Pytest for testing