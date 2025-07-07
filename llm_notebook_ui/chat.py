from __future__ import annotations

from typing import List, Dict

from ipywidgets import VBox, HBox, Textarea, Button, Layout
from IPython.display import display

from .provider import LLMProvider, Message


class LLMChat:
    """Simple interactive chat widget for Jupyter notebooks."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.messages: List[Message] = []
        self.widgets: List[Textarea] = []

        self.input_area = Textarea(placeholder="Type your message", layout=Layout(width='100%'))
        self.send_button = Button(description="Send", button_style='primary')
        self.send_button.on_click(self._on_send)
        self.output_box = VBox()

        controls = HBox([self.input_area, self.send_button])
        self.container = VBox([self.output_box, controls])
        display(self.container)

    # Internal helpers -----------------------------------------------------
    def _add_message(self, role: str, content: str):
        msg: Message = {"role": role, "content": content}
        self.messages.append(msg)
        widget = Textarea(value=content, layout=Layout(width='100%'))
        widget.observe(lambda c, w=widget: self._on_edit(w), names='value')
        self.widgets.append(widget)
        self.output_box.children += (widget,)

    def _on_edit(self, widget: Textarea):
        index = self.widgets.index(widget)
        self.messages[index]['content'] = widget.value

    def _on_send(self, _):
        user_text = self.input_area.value.strip()
        if not user_text:
            return
        self.input_area.value = ''
        self._add_message('user', user_text)
        reply = self.provider.generate(self.messages)
        self._add_message('assistant', reply)
