import asyncio

import streamlit as st

from game import Game

st.set_page_config(layout="wide", page_title="Chameleon", page_icon="🦎")

# CSS
st.markdown("""
<style>
    [data-testid="stVerticalBlock"]:has(div.info_container) [data-testid="stMarkdownContainer"] p { 
        text-align: center;
    }        
    </style>
""", unsafe_allow_html=True)

def display_message(message):
    if message["type"] == "game":
        messages_container.markdown(f"{message['content']}")
    elif message["type"] == "verbose":
        messages_container.markdown(f":green[{message['content']}]")
    elif message["type"] == "debug":
        messages_container.markdown(f":orange[DEBUG: {message['content']}]")

class StreamlitGame(Game):
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
if "game" not in st.session_state:
    st.session_state["game"] = StreamlitGame(verbose=True)

margin_size = 1
center_size = 3

title_left, title_center, title_right = st.columns([margin_size, center_size, margin_size])

with title_center:
    st.markdown("# :rainbow[Chameleon]")

left, center, right = st.columns([margin_size, center_size, margin_size])

with center:
    st.write("Welcome to Chameleon! A deduction and deception game powered by LLMs.")

    start_button = st.button("Start Game")

with right:
    st.markdown("### Player Scores")
    for player in st.session_state["game"].players:
        st.write(f"{player.name}: {player.points}")


messages_container = center.container()

if start_button:
    asyncio.run(st.session_state["game"].start())
