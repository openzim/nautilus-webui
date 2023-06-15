# Contribution

## Dependencies
```bash
# Install all the dependencies.
pipenv sync
# Update dependencies.
pipenv install
```

## Development

If you want to link to Postgresql, create the `.env` file and set the `POSTGRES_URI` environment variable in it, example:

```env
POSTGRES_URI=postgresql+psycopg://username:password@host/database
```

Dev commands:
```bash
# Init database
pipenv run init
# Start FastAPI
pipenv run start
# Run tests
pipenv run tests
# Format code
pipenv run format
# Check format.
pipenv run format:check
```
