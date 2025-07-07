from __future__ import annotations

from typing import List, Dict

from ipywidgets import VBox, HBox, Textarea, Button, Layout
from IPython.display import display

from .provider import LLMProvider, Message



class ChatSession:
    """Maintain editable chat history."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.messages: List[Message] = []

    def add_message(self, role: str, content: str) -> int:
        msg: Message = {"role": role, "content": content}
        self.messages.append(msg)
        return len(self.messages) - 1

    def edit_message(self, index: int, new_content: str) -> None:
        self.messages[index]["content"] = new_content

    def ask(self, prompt: str) -> tuple[str, int]:
        self.add_message("user", prompt)
        reply = self.provider.generate(self.messages)
        idx = self.add_message("assistant", reply)
        return reply, idx


class LLMChat:
    """Simple interactive chat widget for Jupyter notebooks."""

    def __init__(self, provider: LLMProvider, display_widget: bool = True):
        self.session = ChatSession(provider)
        self.widgets: List[Textarea] = []

        self.input_area = Textarea(placeholder="Type your message", layout=Layout(width='100%'))
        self.send_button = Button(description="Send", button_style='primary')
        self.send_button.on_click(self._on_send)
        self.output_box = VBox()

        controls = HBox([self.input_area, self.send_button])
        self.container = VBox([self.output_box, controls])
        if display_widget:
            display(self.container)

    # Internal helpers -----------------------------------------------------
    def _add_message(self, index: int):
        msg = self.session.messages[index]
        widget = Textarea(value=msg["content"], layout=Layout(width="100%"))
        widget.observe(lambda c, i=index: self._on_edit(i, c["new"]), names="value")
        self.widgets.append(widget)
        self.output_box.children += (widget,)

    def _on_edit(self, index: int, new_value: str):
        self.session.edit_message(index, new_value)

    def _on_send(self, _):
        user_text = self.input_area.value.strip()
        if not user_text:
            return
        self.input_area.value = ''
        user_idx = self.session.add_message("user", user_text)
        self._add_message(user_idx)
        reply = self.session.provider.generate(self.session.messages)
        assistant_idx = self.session.add_message("assistant", reply)
        self._add_message(assistant_idx)

    # Public API -----------------------------------------------------------
    def send(self, text: str) -> str:
        """Programmatically send a message and return the reply."""
        user_idx = self.session.add_message("user", text)
        reply = self.session.provider.generate(self.session.messages)
        assistant_idx = self.session.add_message("assistant", reply)
        self._add_message(user_idx)
        self._add_message(assistant_idx)
        return reply
