#!/usr/bin/env python3
#
# Application: Lama
# Comment:     Small script to experiment with conversation history.
# Copyright:   William Andersson 2024
# Website:     https://github.com/william-andersson
# License:     GPL
#
VERSION="0.3.0"
import ollama
import os.path
import os
import sys
import json
import readline

#################### Don't change ####################
StringLen = 0
VERBOSE = False
OPTIONS = {'num_ctx': 4096}
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

def loadDB():
    global HISTORY, SOURCE
    if os.path.exists('%s' % SOURCE):
        with open('%s' % SOURCE, 'r') as db:
            HISTORY = json.load(db)
    else:
        saveDB()

def saveDB():
    global HISTORY, SOURCE
    with open('%s' % SOURCE, 'w') as db:
        json.dump(HISTORY, db)

def format(feed, TermSize):
    # Implement some crude wordwrapping using StringLen, TermSize and size of
    # current and next item.
    global StringLen
    if len(feed) > 1 and len(feed[-1]) != 0:
        if feed[-1][0] != ' ' and \
                StringLen + len(feed[-2]) + len(feed[-1]) > \
                TermSize.columns - 2 and '\n' not in feed[-2]:
            print(f"\n{feed[-2].lstrip()}", end='', flush=True)
            StringLen = len(feed[-2]) - 1
        elif (StringLen + len(feed[-2])) > TermSize.columns - 2:
            print(f"\n{feed[-2].lstrip()}", end='', flush=True)
            StringLen = len(feed[-2]) - 1
        else:
            print(f"{feed[-2]}", end='', flush=True)
            if '\n' in feed[-2]:
                StringLen = 0
            else:
                StringLen += len(feed[-2])
    if len(feed[-1]) == 0:
        if (StringLen + len(feed[-2]) + len(feed[-1]) + 3) > TermSize.columns - 1:
            print(f"\n{feed[-2].lstrip()}{feed[-1]}", end='', flush=True)
        else:
            print(f"{feed[-2]}{feed[-1]}", end='', flush=True)
        StringLen = 0

def run_query():
    global MODEL, OPTIONS, HISTORY, OPTIMIZE, ANTONYM
    answer = ''
    feed = []
    
    stream = ollama.chat(
        model = MODEL,
        messages = HISTORY,
        stream = True,
        options = OPTIONS
    )

    TermSize = os.get_terminal_size()
    for chunk in stream:
        # Collect the output from assistant.
        answer += chunk['message']['content']
        feed.append(chunk['message']['content'])
        if OPTIMIZE != True:
            # Don't print output from optimize function.
            format(feed, TermSize)

    if OPTIMIZE == True:
        return answer
    else:
        text_output = {'role': 'assistant'}
        text_output['content'] = answer
        HISTORY.append(text_output)
    optimize()

def optimize():
    # If history exceeds 95% of num_ctx, compress history stack.
    global HISTORY, OPTIMIZE, OPTIONS, ANTONYM
    limit = int(OPTIONS['num_ctx']*0.95)
    h_size = 0
    
    for i in HISTORY:
        h_size += len(i['content'].split())
    h_size = h_size*2
    if VERBOSE == True:
        print(f"\nlama.py: Token count {h_size}\n")

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

if len(sys.argv) < 3:
    print("Usage: lama.py <model> <conversation_name>")
    sys.exit(1)
else:
    MODEL = sys.argv[1]
    HOME = os.path.expanduser( '~/' )
    if not os.path.exists("%s.lama" % HOME):
        os.makedirs("%s.lama" % HOME)
    SOURCE = HOME + '.lama/' + sys.argv[2]
if sys.argv[-1] == "-v":
    VERBOSE = True
    print(f"lama.py: Running in verbose")
    print(f"lama.py: Using model: {MODEL}")
    print(f"lama.py: Session: {SOURCE}")

loadDB()
while True:
    text_input = {'role': 'user'}
    text_input['content'] = input("\n\n>>> ")
    
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
