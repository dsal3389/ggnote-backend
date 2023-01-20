
# ggnote-backend
ggnote backend is the backend for the ggnote application, this backend should run on a remote
server where you can connect to with the `ggnote-frontend` or `ggnote-cli`

## development

### install
```sh
poetry install
poetry self add poetry-dotenv-plugin
```

### run
```sh
poetry run uvicorn app.main:app --reload
```
