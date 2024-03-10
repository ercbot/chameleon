from typing import Type

import streamlit as st
from streamlit import session_state

from game import Game
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
    session_state.awaiting_human_input = False
    session_state.game_state = "game_start"


class StreamlitInterface(HumanAgentInterface):
    def add_message(self, message: Message):
        super().add_message(message)
        session_state.messages.append(message)
        display_message(message)

    def _generate(self) -> str:
        return session_state.user_input


class StreamlitGame(Game):
    """A Streamlit version of the Game class that uses a state machine to manage the game state."""

    def run_game(self):
        """Starts the game."""

        if session_state.game_state == "game_start":
            self.game_message(fetch_prompt("game_rules"))
            session_state.game_state = "setup_round"
        if session_state.game_state == "setup_round":
            self.setup_round()
            session_state.game_state = "animal_description"
        if session_state.game_state in ["animal_description", "chameleon_guess", "herd_vote"]:
            self.run_round()
        if session_state.game_state == "resolve_round":
            self.resolve_round()
            session_state.game_state = "setup_round"

    def run_round(self):
        """Starts the round."""

        # Phase I: Collect Player Animal Descriptions
        if session_state.game_state == "animal_description":
            for current_player in self.players:
                if current_player.id not in [animal_description['player_id'] for animal_description in self.round_animal_descriptions]:
                    if current_player.interface.is_human:
                        if not session_state.awaiting_human_input:
                            self.game_message(fetch_prompt("player_describe_animal"), current_player)
                            session_state.awaiting_human_input = True
                            break
                        else:
                            self.player_turn_animal_description(current_player)
                            session_state.awaiting_human_input = False
                    else:
                        self.game_message(fetch_prompt("player_describe_animal"), current_player)
                        self.player_turn_animal_description(current_player)
            if len(self.round_animal_descriptions) == len(self.players):
                session_state.game_state = "chameleon_guess"
                session_state.awaiting_human_input = False

        # Phase II: Chameleon Guesses the Animal
        if session_state.game_state == "chameleon_guess":
            self.game_message("All players have spoken. The Chameleon will now guess the secret animal...")
            player_responses = self.format_animal_descriptions(exclude=self.chameleon)
            self.game_message(format_prompt("chameleon_guess_animal", player_responses=player_responses), self.chameleon)
            if self.players[self.human_index].role == "chameleon":
                if not session_state.awaiting_human_input:
                    session_state.awaiting_human_input = True
                else:
                    self.player_turn_chameleon_guess(self.chameleon)
                    session_state.awaiting_human_input = False
            else:
                self.player_turn_chameleon_guess(self.chameleon)
                session_state.awaiting_human_input = False

            session_state.game_state = "herd_vote"

        # Phase III: The Herd Votes for who they think the Chameleon is
        if session_state.game_state == "herd_vote":
            for current_player in self.players:
                if current_player.role == "herd" and current_player.id not in [vote['voter_id'] for vote in self.herd_vote_tally]:
                    player_responses = self.format_animal_descriptions(exclude=current_player)
                    if current_player.interface.is_human:
                        if not session_state.awaiting_human_input:
                            self.game_message(format_prompt("vote", player_responses=player_responses), current_player)
                            session_state.awaiting_human_input = True
                            break
                        else:
                            self.player_turn_herd_vote(current_player)
                            session_state.awaiting_human_input = False
                    else:
                        self.game_message(format_prompt("vote", player_responses=player_responses), current_player)
                        self.player_turn_herd_vote(current_player)

            if len(self.herd_vote_tally) == len(self.players) - 1:
                session_state.game_state = "resolve_round"


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
        st.session_state.game = StreamlitGame(human_name=user_input, verbose=True, human_interface=StreamlitInterface)
    session_state.user_input = user_input
    st.session_state.game.run_game()


footer="""<style>
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
text-align: center;
}
</style>
<div class="footer">
<p>Created by <a href="https://huggingface.co/ericbotti" target="_blank">Eric Botti</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)