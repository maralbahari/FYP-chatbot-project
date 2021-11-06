FROM rasa/rasa-sdk:2.8.1

WORKDIR /app

COPY actions/requirements.txt ./

COPY actions/service_key.json ./

USER root

COPY ./actions /app/actions

CMD ["start", "--actions", "actions"]

RUN pip install -r requirements.txt

EXPOSE 5055

ENTRYPOINT ["./entrypoint.sh"]

USER 1000
