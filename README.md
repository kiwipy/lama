# Ollama chat experiment
> [!NOTE]
> This script expects that you already have [Ollama](https://github.com/ollama/ollama) installed

This is a small test script to experiment with chat history in Ollama.<br>
The script uses a content window of 4096 tokens as default and the llama3.2 model.
When the history stack reaches 95% of num_ctx it compresses the history stack to
allow for larger conversations with referenced history. It does this by asking the model
to compress the history in the background then transform the output as if it were entered
by the user and add it to a new empty stack as a user input.

## Usage
Run **`./lama.py <conversation_name>`**
