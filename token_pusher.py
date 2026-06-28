name: ITV Token Pusher

on:
  schedule:
    - cron: '*/8 * * * *'  # Har 8 daqiqada (token 60 min, scan 4 min)
  workflow_dispatch:

jobs:
  push-tokens:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Python o'rnatish
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Kutubxona o'rnatish
        run: pip install requests

      - name: Tokenlarni yangilash
        env:
          WORKER_URL: ${{ secrets.WORKER_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
        run: python token_pusher.py
