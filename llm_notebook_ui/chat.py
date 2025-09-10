from __future__ import annotations

from typing import List, Dict

from ipywidgets import VBox, HBox, Textarea, Button, Layout
from IPython.display import display

from .provider import LLMProvider, Message



class ChatSession:
    """Maintain editable chat history for a conversation."""

    def __init__(self, provider: LLMProvider):
        """Create a new chat session bound to *provider*."""
        self.provider = provider
        # Messages are stored as a list of ``{"role": str, "content": str}``.
        self.messages: List[Message] = []

    def add_message(self, role: str, content: str) -> int:
        """Append a message and return its index."""
        msg: Message = {"role": role, "content": content}
        self.messages.append(msg)
        return len(self.messages) - 1

    def edit_message(self, index: int, new_content: str) -> None:
        """Update a previously stored message."""
        self.messages[index]["content"] = new_content

    def ask(self, prompt: str) -> tuple[str, int]:
        """Send *prompt* and return ``(reply, index)`` of the response."""
        self.add_message("user", prompt)
        reply = self.provider.generate(self.messages)
        idx = self.add_message("assistant", reply)
        return reply, idx


class LLMChat:
    """Simple interactive chat widget for Jupyter notebooks."""

    def __init__(self, provider: LLMProvider, display_widget: bool = True):
        """Create and optionally display the chat widget."""
        self.session = ChatSession(provider)
        self.widgets: List[Textarea] = []

        # User input components -------------------------------------------------
        self.input_area = Textarea(
            placeholder="Type your message", layout=Layout(width="100%")
        )
        self.send_button = Button(description="Send", button_style="primary")
        self.send_button.on_click(self._on_send)
        self.output_box = VBox()

        controls = HBox([self.input_area, self.send_button])
        self.container = VBox([self.output_box, controls])
        if display_widget:
            display(self.container)

    # Internal helpers -----------------------------------------------------
    def _add_message(self, index: int):
        """Create a Textarea widget for message ``index`` and display it."""
        msg = self.session.messages[index]
        widget = Textarea(value=msg["content"], layout=Layout(width="100%"))
        widget.observe(
            lambda c, i=index: self._on_edit(i, c["new"]), names="value"
        )
        self.widgets.append(widget)
        self.output_box.children += (widget,)

    def _on_edit(self, index: int, new_value: str):
        """Callback when a widget's text changes."""
        self.session.edit_message(index, new_value)

    def _on_send(self, _):
        """Handle clicks on the Send button."""
        user_text = self.input_area.value.strip()
        if not user_text:
            return
        self.input_area.value = ""
        user_idx = self.session.add_message("user", user_text)
        self._add_message(user_idx)
        reply = self.session.provider.generate(self.session.messages)
        assistant_idx = self.session.add_message("assistant", reply)
        self._add_message(assistant_idx)

    # Public API -----------------------------------------------------------
    def send(self, text: str) -> str:
        """Programmatically send ``text`` and return the model's reply."""
        user_idx = self.session.add_message("user", text)
        reply = self.session.provider.generate(self.session.messages)
        assistant_idx = self.session.add_message("assistant", reply)
        self._add_message(user_idx)
        self._add_message(assistant_idx)
        return reply
