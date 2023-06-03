## INIT

use `requirements.txt` to install the dependencies

-> `pip freeze requirements.txt`
-> `pip install -r requirements.txt`

## RUN [DEVELOPMENT]

- Activate the environment

  - `py -3 -m venv .venv`
  - `.venv\Scripts\activate`

- `flask run`

## BUILD AND DEPLOY

### Gunicorn

`python -m venv .venv`
`.venv\Scripts\activate`
`pip install . # install your application`
`pip install gunicorn`

### BUILD

`pip install build`
`python -m build --wheel`

1. python -m build

.env template

```
API_KEY=abc123
BASE_URL=https://api.data
```
