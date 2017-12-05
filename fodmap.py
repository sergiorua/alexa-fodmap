#!/usr/bin/env python

import os
import sys
import yaml
import logging
import itertools

from flask import Flask
from flask_ask import Ask, statement, question, session

DEBUG = True
Version = '1.0.0'
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = DEBUG
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

if DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/tmp/fodmap.log',
                    filemode='w')

# load fodmap lists
FodMap = {}
for l in ['high_fodmap.yaml', 'low_fodmap.yaml']:
    if os.path.exists(l):
        with open(l, 'r') as f:
            name = l.replace('_fodmap.yaml','')
            FodMap[name] = yaml.load(f)


@ask.launch
def start_skill():
    welcome_message = 'To check the FODMAP database just ask, for example, if carrots are fodmap.'
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
    help_msg = 'For example, ask me: are carrots low fodmap?'
    return statement(help_msg).simple_card('fodmapHelpIntent', help_msg)

@ask.intent('fodmapCheckIntent',
        mapping={
            'food1': 'FoodFirst',
            'food2': 'FoodSecond',
            'food3': 'FoodThird',
            'grade': 'Grade',
            'category': 'Category'
        },
        default={
            'food1': '',
            'food2': '',
            'food3': '',
            'grade': '',
            'category': 'General'
            })
def intent_check(food1, food2, food3, grade, category):
    req_food = "%s %s %s" % (food1, food2, food3)
    err_msg = None
    if req_food == '' or len(req_food) < 2:
        err_msg = 'Sorry, I do not know that foodstuff'

    if err_msg:
        return statement(err_msg).simple_card('fodmapCheckIntentError', err_msg)

    if is_fodmap(food1, food2, food3, 'low'):
        answer_msg = "%s is in the low fodmap category" % (req_food)
    elif is_fodmap(food1, food2, food3, 'high'):
        answer_msg = "%s is classified as high fodmap" % (req_food)
    else:
        answer_msg = "Sorry but %s is not in my lists" % (req_food)

    logging.debug(answer_msg)
    return statement(answer_msg).simple_card('fodmapCheckIntentReply', answer_msg)

#####
def build_words(food1, food2, food3):
    words = []
    word_list = filter(len, [food1, food2, food3])
    for p in itertools.permutations(word_list):
        words.append(" ".join(p).lower())
    return words

def is_fodmap(food1, food2, food3, l='low_fodmap'):
    for food in build_words(food1, food2, food3):
        if food in FodMap[l]:
            return True
    return False

if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=DEBUG)

# vim: ts=4 expandtab ft=python
