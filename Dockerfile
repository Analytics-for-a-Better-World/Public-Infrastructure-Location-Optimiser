FROM python:3.10-buster
COPY . /app
WORKDIR /app
RUN pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Install pandana separately to prevent poetry error
RUN python -m pip install "pandana @ git+https://github.com/UDST/pandana@1e3920f3fbc1d17074d1881683adce96d0192bb1"
EXPOSE 8501
RUN mkdir ~/.streamlit
RUN cp config.toml ~/.streamlit/config.toml
RUN cp credentials.toml ~/.streamlit/credentials.toml
WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["gpbp_app/main_page.py"]