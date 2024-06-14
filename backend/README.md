# backend

Leverages great things to achieve great results

[![CodeFactor](https://www.codefactor.io/repository/github/openzim/nautilus-webui/badge)](https://www.codefactor.io/repository/github/openzim/nautilus-webui)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![codecov](https://codecov.io/gh/openzim/nautilus-webui/branch/main/graph/badge.svg)](https://codecov.io/gh/openzim/nautilus-webui)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fgithub.com%2Fopenzim%2Fnautilus-webui%2Fraw%2Fmain%2Fbackend%2Fpyproject.toml)


## Usage

**CAUTION**: this is not a standalone, installable Python package.

- It's the backend of a web service that is intended to be deployed using OCI images.
- See the sample Composefile in the dev folder of the repository.
- It has external dependencies (including [S3 Storage](https://wasabi.com/), [Mailgun](https://www.mailgun.com/) account and a full-fledged [Zimfarm](https://github.com/openzim/zimfarm).
- It **must be configured** via environment variables (see `constants.py` and Compose's Envfile)
- There is no CHANGELOG nor release management. Production is tied to CD on `main` branch.

```sh
❯ hatch run serve
```

nautilus-webui backend adheres to openZIM's [Contribution Guidelines](https://github.com/openzim/overview/wiki/Contributing).

nautilus-webui backend has implemented openZIM's [Python bootstrap, conventions and policies](https://github.com/openzim/_python-bootstrap/docs/Policy.md) **v1.0.1**.
