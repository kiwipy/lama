# Ollama chat experiment
> [!NOTE]
> This script expects that you already have [Ollama](https://github.com/ollama/ollama) installed

> [!IMPORTANT]
> This repository is experimental, the code my change drastically,
> although it might develop into something eventually.

This is a small test script to experiment with chat history in Ollama.<br>
The script uses a content window of 4096 tokens as default.
When the history stack reaches 95% of num_ctx it compresses the history stack to
allow for larger conversations with referenced history. It does this by asking the model
to compress the history in the background then transform the output as if it were entered
by the user and add it to a new empty stack as a user input.

## Usage
Run **`./lama.py <model> <conversation_name>`**<br>
- Use the UP arrow to resend the last request, this will remove the last answer and replace it with a new.<br>
- Type /bye to exit and save.
