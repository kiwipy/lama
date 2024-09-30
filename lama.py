#!/usr/bin/env python3
#
# Application: Lama
# Comment:     Small script to experiment with conversation history.
# Copyright:   William Andersson 2024
# Website:     https://github.com/william-andersson
# License:     GPL
#
VERSION="0.1.0"
import ollama
import os.path
import sys
import json
import readline

MODEL = "llama3.2"
OPTIONS = {'num_ctx': 4096}

#################### Don't change ####################
HISTORY = []
OPTIMIZE = False
ANTONYM = {'I': 'you', 'me': 'you',
           'you': 'I', 'You': 'I',
           'your': 'my', 'my': 'your',
           'yours': 'mine', 'mine': 'yours',
           'you\'d': 'I\'d', 'I\'d': 'you\'d',
           'you\'re': 'I\'m', 'I\'m': 'you\'re',
           'yourself': 'myself', 'myself': 'yourself'}
######################################################

if len(sys.argv) < 2:
    print("Usage: lama.py <conversation_name>")
    sys.exit(1)
else:
    SOURCE = sys.argv[1]

def loadDB():
    global HISTORY, SOURCE
    if os.path.exists('%s.db' % SOURCE):
        with open('%s.db' % SOURCE, 'r') as db:
            HISTORY = json.load(db)
    else:
        saveDB()

def saveDB():
    global HISTORY, SOURCE
    with open('%s.db' % SOURCE, 'w') as db:
        json.dump(HISTORY, db)

def run_query():
    global MODEL, OPTIONS, HISTORY, OPTIMIZE, ANTONYM
    answer = ''
    
    stream = ollama.chat(
        model = MODEL,
        messages = HISTORY,
        stream = True,
        options = OPTIONS
    )

    for chunk in stream:
        # Collect the output from assistant.
        answer += chunk['message']['content']
        if OPTIMIZE != True:
            # Don't print output from optimize function.
            print(chunk['message']['content'], end='', flush=True)
    if OPTIMIZE == True:
        return answer
    else:
        text_output = {'role': 'assistant'}
        text_output['content'] = answer
        HISTORY.append(text_output)
    optimize()

def optimize():
    # If history exceeds 95% of num_ctx, compress history stack.
    global HISTORY, OPTIMIZE, OPTIONS
    limit = int(OPTIONS['num_ctx']*0.95)
    h_size = 0
    
    for i in HISTORY:
        h_size += len(i['content'].split())
    h_size = h_size*2

    if h_size >= limit:
        OPTIMIZE = True
        print("\n[Optimizing history stack...]")
        CmdPrompt = {'role': 'user', 'content': 'compress conversation history'}
        HISTORY.append(CmdPrompt)
        answer = run_query()
        text_output = {'role': 'user'}
        HISTORY = []
        OPTIMIZE = False
        answer_mod = ''
        for i in answer.split():
            # Optimize history by switching 'assistant' for 'user' to create a
            # new history stack where the compressed conversation history is
            # promted AS 'user'. This way the assistant can keep reffering to
            # the conversation.
            if i in ANTONYM:
                answer_mod += ANTONYM[i]
                answer_mod += ' '
            else:
                answer_mod += i
                answer_mod += ' '
        text_output['content'] = answer_mod
        HISTORY.append(text_output)

loadDB()
while True:
    text_input = {'role': 'user'}
    text_input['content'] = input("\n>>> ")
    
    if text_input['content'] == "/bye":
        break
    elif len(HISTORY) >2 and text_input['content'] == HISTORY[-2]['content']:
        # Arrow up to resend the previous promt,
        # this will remove previous answer from history
        HISTORY.pop()
        run_query()
    else:
        HISTORY.append(text_input)
        run_query()
saveDB()
