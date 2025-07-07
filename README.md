# LLM Notebook UI

This project provides a simple Jupyter-based interface for chatting with Large Language Models (LLMs). The chat widget allows you to edit both the prompts you send and the responses from the model. Any edits immediately update the conversation history so that subsequent model calls use the modified text.

## Features

- Interactive chat widget that works directly in Jupyter notebooks.
- Editable messages and model responses.
- Pluggable provider system supporting:
  - OpenAI ChatGPT
  - Google Gemini
  - Ollama (local models)
- Easily extensible for other providers.

## Installation

Install the required packages in your environment:

```bash
pip install ipywidgets openai google-generativeai requests nbformat
```

## Usage

There are two ways to interact with the models:

### Chat widget

Create a notebook and instantiate the chat UI with your provider of choice:

```python
from llm_notebook_ui import OpenAIProvider, LLMChat

# Configure provider (expects `OPENAI_API_KEY` environment variable)
provider = OpenAIProvider()

# Display the chat widget
chat = LLMChat(provider)
```

Try editing any message in the conversation; the history stored by the widget will be updated so future replies take those edits into account.

### Chat cell

Load the IPython extension and create cells starting with `%%chat`:

```python
%load_ext llm_notebook_ui.magics
```

```python
%%chat
What is the capital of France?
```

The response appears in an editable text area. Edits are stored in the conversation context so the next `%%chat` cell uses your modified text.

See `examples/chat_example.ipynb` for a minimal working notebook.
