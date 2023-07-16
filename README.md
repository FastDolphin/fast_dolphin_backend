# Fast Dolphin Backend

This repository contains a FastAPI service, which is used to handle customer requests and interact with a MongoDB database. The services are containerized using Docker.

## Services

The application consists of the following services:

- `api`: This is the FastAPI application. It is used to handle HTTP requests from clients and to interact with the MongoDB database.

- `mongodb`: This is the MongoDB database. It is used to persistently store data for the application.

The API service will be available at `http://localhost:8000`.

## GitHub Actions

This repository uses GitHub Actions to automatically build a Docker image for the `api` service whenever a pull request is made to the `master` branch.

## Endpoints

The API service has the following endpoints:

- `POST /`: Create a new request.
- `GET /`: Get all entries in the database.
- `DELETE /{id}`: Delete an entry based on the entry's ID.

## Environment Variables

The application uses the following environment variables:

- `MONGO_ADDRESS`: This is the connection string for the MongoDB database. It should be in the format `mongodb://username:password@mongo:27017`.

- `DB_NAME`: This is the name of the MongoDB database.

These environment variables can be set in a `.env` file at the root of the repository.

## Contributing

If you want to contribute to this project, please create a new branch, make your changes, and create a pull request. Ensure that the GitHub Actions workflow passes before merging your pull request.
