FROM rasa/rasa-sdk:2.8.1

WORKDIR /app

# COPY actions/requirements.txt ./

USER root

COPY ./actions /app/actions
CMD  ["start", "actions", "--actions", "--debug"]
#RUN pip install -r requirements.txt

USER 1000
