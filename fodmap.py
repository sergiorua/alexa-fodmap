#!/usr/bin/env python

import os
import logging
from flask import Flask
from flask_ask import Ask, statement, question, session

DEBUG = False
Version = '1.0.0'
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = DEBUG
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

if DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/tmp/myapp.log',
                    filemode='w')

@ask.launch
def start_skill():
    welcome_message = 'Hello.'
    return statement(welcome_message)

@ask.intent('AMAZON.StopIntent')
def stop():
    return statement("Goodbye")

@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement("Goodbye")

@ask.session_ended
def session_ended():
    return "{}", 200

@ask.intent('fodmapHelpIntent')
def intent_help():
    help_msg = 'Are carrots low fodmap?'
    return statement(help_msg).simple_card('fodmapHelpIntent', help_msg)

@ask.intent('fodmapCheckIntent',
        mapping={'food': 'Food', 'category': 'Category'},
        default={'food': '', 'category': 'General'}
        )
def intent_check(food, category):
    err_msg = None
    if food == '':
        err_msg = 'Sorry, I do not know that foodstuff'

    if err_msg:
        return statement(err_msg).simple_card('bakeConverterError', err_msg)

    logging.debug(answer_msg)
    return statement(answer_msg).simple_card('bakeConverterReply', answer_msg)


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=DEBUG)

# vim: ts=4 expandtab
