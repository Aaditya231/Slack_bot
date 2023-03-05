import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']


class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Create meet using below link \n\n'
                '*https://meet.jit.si*'
            )
        }
    }
    DIVIDER = {'type': 'divider'}

    def __init__(self, channel, user):
        self.user = user
        self.channel = channel
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False

    def get_message(self):
        return{
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome Bot',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER
                

            ]
        }
    
   

message_counts = {}
welcome_messages = {}


def send_welcome_message(channel, user):
    welcome = WelcomeMessage(channel, user)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    welcome_messages[channel][user] = welcome


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if user_id != None and BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1

        if text.lower() == 'meet':
            send_welcome_message(channel_id, user_id)
            #send_welcome_message(f'@{user_id}', user_id) for DM's


@app.route('/meet', methods=['GET', 'POST'])
def message():
    data = request.form
    channel_id = data.get('Channel_id')
    text = f"https://meet.jit.si"
    client.chat_postMessage(channel=channel_id, text=text)
    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
