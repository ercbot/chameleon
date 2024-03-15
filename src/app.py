from typing import Type

import streamlit as st
from streamlit import session_state

from game_chameleon import ChameleonGame
from agent_interfaces import HumanAgentInterface
from message import Message
from prompts import fetch_prompt, format_prompt

st.set_page_config(layout="wide", page_title="Chameleon")


def display_message(message: Message):
    if message.type == "verbose":
        messages_container.markdown(f":green[{message.content}]")
    elif message.type == "debug":
        messages_container.markdown(f":orange[DEBUG: {message.content}]")
    else:
        messages_container.markdown(f"{message.content}")


if "messages" not in session_state:
    session_state.messages = []
    session_state.user_input = None


class StreamlitInterface(HumanAgentInterface):
    def add_message(self, message: Message):
        super().add_message(message)
        session_state.messages.append(message)
        display_message(message)

    def _generate(self) -> str:
        response = session_state.user_input
        session_state.user_input = None
        return response


# Streamlit App

margin_size = 1
center_size = 3

title_left, title_center, title_right = st.columns([margin_size, center_size, margin_size])

with title_center:
    st.markdown("# :rainbow[Chameleon]")

left, center, right = st.columns([margin_size, center_size, margin_size])

with center:
    messages_container = st.container()

    messages_container.write("Welcome to Chameleon! A social deduction game powered by LLMs.")

    messages_container.write("Enter your name to begin...")

    user_input = st.chat_input("Your response:")

    if st.session_state.messages:
        for message in st.session_state.messages:
            display_message(message)

if user_input:
    if "game" not in st.session_state:
        st.session_state.game = ChameleonGame.from_human_name(user_input, StreamlitInterface)
    else:
        session_state.user_input = user_input

    st.session_state.game.run_game()

st.markdown("#")

footer="""<style>
.footer {
position: fixed;
background-color: #0E1117;
padding-top: 10px;
left: 0;
bottom: 0;
width: 100%;
text-align: center;
}
</style>
<div class="footer">
<p style="margin: 0;">Created by <a href="https://huggingface.co/ericbotti" target="_blank">Eric Botti</a></p>
<small>Your responses may be collected for research purposes</small>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)