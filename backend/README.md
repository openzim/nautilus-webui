# Contribution

## Dependencies
```bash
# Install all the dependencies.
pipenv sync
# Update dependencies.
pipenv install
```

## Development

Since we used the `psycopg2` instead of the `psycopg2-binary`, you should install the Postgresql on your machine. Please read the [document](https://www.psycopg.org/docs/install.html#prerequisites) of `psycopg2`

If you want to link to Postgresql, create the `.env` file and set the `DATABASE_URL` environment variable in it, example:

```env
DATABASE_URL=postgresql+psycopg2://username:password@host/database
```

Dev commands:
```bash
# Start FastAPI
pipenv run start
# Run tests
pipenv run tests
# Format code
pipenv run format
# Check format.
pipenv run format:check
```
