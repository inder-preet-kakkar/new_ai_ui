from __future__ import annotations

"""IPython magics providing a ``%%chat`` cell magic."""

from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.display import display, Markdown
from ipywidgets import Textarea, Layout
from IPython import get_ipython

from .provider import LLMProvider, OpenAIProvider
from .chat import ChatSession


@magics_class
class ChatMagics(Magics):
    """Provide ``%%chat`` cell magic for editable conversations."""

    def __init__(self, shell, provider: LLMProvider | None = None):
        """Create a new ``ChatMagics`` instance.

        Parameters
        ----------
        shell:
            The IPython shell instance.
        provider:
            Optional :class:`~llm_notebook_ui.provider.LLMProvider` to use for
            generating responses. If omitted, :class:`OpenAIProvider` is used.
        """
        super().__init__(shell)
        self.session = ChatSession(provider or OpenAIProvider())

    @cell_magic
    def chat(self, line: str, cell: str):
        """Execute the cell as a chat prompt.

        The returned value is an editable :class:`ipywidgets.Textarea` containing
        the model's response. Editing the text updates the stored conversation so
        future prompts use the modified text. If widgets cannot be rendered, a
        ``Markdown`` object is returned instead.
        """
        prompt = cell.strip()
        if not prompt:
            return
        reply, idx = self.session.ask(prompt)
        try:
            widget = Textarea(value=reply, layout=Layout(width="100%"))
            widget.observe(
                lambda c, i=idx: self.session.edit_message(i, c["new"]),
                names="value",
            )
            # Returning the widget makes it appear as regular cell output
            return widget
        except Exception:  # pragma: no cover - fallback when widgets unavailable
            return Markdown(reply)


def load_chat_magics(provider: LLMProvider) -> None:
    """Register the ``%%chat`` cell magic using the given provider."""
    ip = get_ipython()
    if ip is None:
        raise RuntimeError("load_chat_magics must run inside IPython")
    ip.register_magics(ChatMagics(ip, provider))


def load_ipython_extension(ip):
    """Entry point for ``%load_ext`` using the :class:`OpenAIProvider`."""
    ip.register_magics(ChatMagics(ip, OpenAIProvider()))
