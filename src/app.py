import asyncio
from time import sleep

import streamlit as st
from langchain_core.messages import AIMessage

from game import Game

st.set_page_config(layout="wide", page_title="Chameleon", page_icon="img/logo.svg")
human_turn = False


def display_message(message):
    if message["type"] == "game":
        messages_container.markdown(f"{message['content']}")
    elif message["type"] == "verbose":
        messages_container.markdown(f":green[{message['content']}]")
    elif message["type"] == "debug":
        messages_container.markdown(f":orange[DEBUG: {message['content']}]")


class StreamlitGame(Game):
    @staticmethod
    async def human_input(prompt: str) -> str:
        _user_input = st.chat_input("Your message", key=f"user_input_{st.session_state.user_input_id}")
        st.session_state.user_input_id += 1

        while _user_input is None or _user_input == "":
            sleep(0.1)

        print(f"User input: {_user_input}")

        response = AIMessage(content=_user_input)

        return response

    def human_message(self, message: str):
        message = {"type": "game", "content": message}
        st.session_state["messages"].append(message)
        display_message(message)

    def verbose_message(self, message: str):
        if self.verbose:
            message = {"type": "verbose", "content": message}
            st.session_state["messages"].append(message)
            display_message(message)

    def debug_message(self, message: str):
        if self.debug:
            message = {"type": "debug", "content": message}
            st.session_state["messages"].append(message)
            display_message(message)


if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "game_started" not in st.session_state:
    st.session_state["game_started"] = False
if "user_input_id" not in st.session_state:
    st.session_state["user_input_id"] = 0

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

    if st.session_state.messages:
        for message in st.session_state.messages:
            display_message(message)

    user_input = st.chat_input("Your message")
    st.session_state.user_input_id += 1

if not st.session_state.game_started and user_input:
    st.session_state.game_started = True
    if "game" not in st.session_state:
        st.session_state.game = StreamlitGame(human_name=user_input, verbose=True)

    asyncio.run(st.session_state.game.start())


