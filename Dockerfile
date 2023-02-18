FROM python:3.10-slim
COPY . /app
WORKDIR /app
# RUN curl -sSL https://install.python-poetry.org | python3 -
RUN pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

RUN mkdir ~/.streamlit
RUN cp config.toml ~/.streamlit/config.toml
RUN cp credentials.toml ~/.streamlit/credentials.toml
WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["gpbp_app/main_page.py"]