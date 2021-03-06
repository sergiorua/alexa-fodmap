#!/usr/bin/env python

import os
import sys
import yaml
import logging
import itertools
import inflect

from flask import Flask
from flask_ask import Ask, statement, question, session

DEBUG = True
Version = '1.0.0'
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = DEBUG
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
inflect = inflect.engine()

if DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/tmp/fodmap.log',
                    filemode='w')
def is_are(f):
    if inflect.singular_noun(f):
        return 'are'
    return 'is'

# load fodmap lists
FodMap = {}
for l in ['high_fodmap.yaml', 'low_fodmap.yaml']:
    if os.path.exists(l):
        with open(l, 'r') as f:
            name = l.replace('_fodmap.yaml','')
            FodMap[name] = yaml.load(f)


@ask.launch
def start_skill():
    welcome_prompt = 'Welcome. Please ask me to check a food by saying, check if broccoli is FODMAP'
    welcome_reprompt = 'Please ask me to check a food by saying, check if broccoli is FODMAP'
    return question(welcome_prompt).reprompt(welcome_reprompt).simple_card('FODMAP Welcome', welcome_prompt)

@ask.intent('AMAZON.StopIntent')
@ask.intent('AMAZON.CancelIntent')
@ask.intent('AMAZON.NoIntent')
def cancel():
    return statement("Goodbye")

@ask.on_session_started
def new_session():
    logging.info('new session started')

@ask.session_ended
def session_ended():
    return '{}', 200

@ask.intent('fodmapHelpIntent')
def intent_help():
    help_msg = 'For example, ask me: are carrots fodmap?'
    return question(help_msg).simple_card('FODMAP Help', help_msg)

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
    req_food = req_food.rstrip(' ')
    session.attributes['FOOD'] = req_food
    err_msg = None
    if req_food == '' or len(req_food) < 2:
        err_msg = 'Sorry, I do not know that foodstuff'

    if err_msg:
        return statement(err_msg).simple_card('FODMAP Check', err_msg)

    if is_fodmap(food1, food2, food3, 'low'):
        answer_msg = "%s %s in the low FODMAP category" % (req_food, is_are(req_food))
    elif is_fodmap(food1, food2, food3, 'high'):
        answer_msg = "%s %s classified as high FODMAP" % (req_food, is_are(req_food))
    else:
        answer_msg = "Sorry but %s %s not in my lists" % (req_food, is_are(req_food))

    logging.debug(answer_msg)
    return statement(answer_msg).simple_card('FODMAP Check', answer_msg)

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
