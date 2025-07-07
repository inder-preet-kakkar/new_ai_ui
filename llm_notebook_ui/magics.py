from __future__ import annotations

from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.display import display
from ipywidgets import Textarea, Layout
from IPython import get_ipython

from .provider import LLMProvider, OpenAIProvider
from .chat import ChatSession


@magics_class
class ChatMagics(Magics):
    """Provide %%chat cell magic for editable conversations."""

    def __init__(self, shell, provider: LLMProvider | None = None):
        super().__init__(shell)
        self.session = ChatSession(provider or OpenAIProvider())

    @cell_magic
    def chat(self, line: str, cell: str) -> None:
        prompt = cell.strip()
        if not prompt:
            return
        reply, idx = self.session.ask(prompt)
        widget = Textarea(value=reply, layout=Layout(width="100%"))
        widget.observe(lambda c, i=idx: self.session.edit_message(i, c["new"]), names="value")
        display(widget)


def load_chat_magics(provider: LLMProvider) -> None:
    """Register the chat cell magic with a custom provider."""
    ip = get_ipython()
    if ip is None:
        raise RuntimeError("load_chat_magics must run inside IPython")
    ip.register_magics(ChatMagics(ip, provider))


def load_ipython_extension(ip):
    """Default extension entry point using OpenAI provider."""
    ip.register_magics(ChatMagics(ip, OpenAIProvider()))
