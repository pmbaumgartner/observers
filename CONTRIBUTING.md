# Contributing

## Development

We use [PDM](https://pdm-project.org/en/latest/) to manage dependencies and virtual environments. Make sure you have it installed and then run:

```bash
pdm install
```

## Publishing

Configure the PyPI credentials through environment variables `PDM_PUBLISH_USERNAME="__token__"` and `PDM_PUBLISH_PASSWORD=<your-pypi-token>` and run:

```bash
pdm publish
```
