import streamlit as st
import json
import os
from collections import Counter


# Initialize session state
def initialize_session_state():
    if 'code_variants' not in st.session_state:
        st.session_state.code_variants = []
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 1
    if 'voting_results' not in st.session_state:
        st.session_state.voting_results = Counter()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'add_code'
    if 'remaining_variants' not in st.session_state:
        st.session_state.remaining_variants = []
    if 'current_pair_index' not in st.session_state:
        st.session_state.current_pair_index = 0
    if 'next_round_variants' not in st.session_state:
        st.session_state.next_round_variants = []
    if 'competition_id' not in st.session_state:
        st.session_state.competition_id = 1
    if 'pairs' not in st.session_state:
        st.session_state.pairs = []


# Function to save the voting state
def save_voting_state():
    voting_state = {
        'code_variants': st.session_state.code_variants,
        'current_round': st.session_state.current_round,
        'voting_results': dict(st.session_state.voting_results),
        'remaining_variants': st.session_state.remaining_variants,
        'current_pair_index': st.session_state.current_pair_index,
        'next_round_variants': st.session_state.next_round_variants,
        'pairs': st.session_state.pairs
    }

    file_path = "competitions/current_voting_state.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as file:
        json.dump(voting_state, file)


# Function to load the voting state
def load_voting_state():
    file_path = "competitions/current_voting_state.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                voting_state = json.load(file)

            st.session_state.code_variants = voting_state['code_variants']
            st.session_state.current_round = voting_state['current_round']
            st.session_state.voting_results = Counter(voting_state['voting_results'])
            st.session_state.remaining_variants = voting_state['remaining_variants']
            st.session_state.current_pair_index = voting_state['current_pair_index']
            st.session_state.next_round_variants = voting_state['next_round_variants']
            st.session_state.pairs = voting_state['pairs']

            if st.session_state.current_round > 1 and not st.session_state.remaining_variants:
                st.warning("Previous round is finished. Proceeding to the next round.")
                init_voting_round()
                next_page()
                st.rerun()

            st.success("Voting state restored successfully!")
        except json.JSONDecodeError:
            st.error("Error loading voting state. The file might be corrupted.")
    else:
        st.warning("No previous voting state found.")


# Function to clear voting state after competition ends
def clear_voting_state():
    file_path = "competitions/current_voting_state.json"
    if os.path.exists(file_path):
        os.remove(file_path)


# Function to save the competition state to a file
def save_competition_state():
    competition_data = {
        'code_variants': st.session_state.code_variants,
        'current_round': st.session_state.current_round,
        'voting_results': dict(st.session_state.voting_results),
        'remaining_variants': st.session_state.remaining_variants,
        'current_pair_index': st.session_state.current_pair_index,
        'next_round_variants': st.session_state.next_round_variants
    }

    file_path = "competitions/all_competitions.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                all_competitions = json.load(file)
        except json.JSONDecodeError:
            st.error("Error loading competition data. File might be corrupted.")
            all_competitions = []
    else:
        all_competitions = []

    all_competitions.append(competition_data)

    with open(file_path, 'w') as file:
        json.dump(all_competitions, file)

    st.session_state.competition_id += 1
    st.success(f"Competition {st.session_state.competition_id} saved successfully!")


# Display saved competitions
def display_saved_competitions():
    st.title("Saved Competitions")

    file_path = "competitions/all_competitions.json"

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                all_competitions = json.load(file)

            if all_competitions:
                for idx, competition in enumerate(all_competitions, 1):
                    if st.button(f"Competition {idx}"):
                        st.session_state.code_variants = competition['code_variants']
                        st.session_state.current_round = competition['current_round']
                        st.session_state.voting_results = Counter(competition['voting_results'])
                        st.session_state.remaining_variants = competition['remaining_variants']
                        st.session_state.current_pair_index = competition['current_pair_index']
                        st.session_state.next_round_variants = competition['next_round_variants']
                        next_page()
                        st.rerun()

                if st.button("Clear"):
                    os.remove(file_path)
                    st.success("All saved competitions have been deleted.")
                    st.rerun()
            else:
                st.write("No competitions saved yet.")
        except json.JSONDecodeError:
            st.error("Error loading saved competitions. File might be corrupted.")
    else:
        st.write("No competitions saved yet.")

    if st.button("Back to Add Code"):
        st.session_state.code_variants = []
        st.session_state.voting_results = Counter()
        st.session_state.remaining_variants = []
        st.session_state.current_pair_index = 0
        st.session_state.next_round_variants = []
        st.session_state.current_page = 'add_code'
        clear_voting_state()
        st.rerun()


# Function to initialize the voting round
def init_voting_round():
    st.session_state.remaining_variants = st.session_state.code_variants.copy()
    st.session_state.current_round = 1
    st.session_state.voting_results.clear()
    st.session_state.current_pair_index = 0
    st.session_state.next_round_variants = []


# Add a page flow to include the saved competitions page
def next_page():
    page_flow = {
        'add_code': 'voting',
        'voting': 'results',
        'results': 'saved_competitions',
    }
    st.session_state.current_page = page_flow.get(st.session_state.current_page, 'results')


# Handle code addition
def add_code():
    st.title("Add Your Code")
    code_input = st.text_area("Your Code", value="")

    if st.button("Add", key="add_code_button"):
        if code_input.strip():
            st.session_state.code_variants.append(code_input)
            st.success("Code variant added.")
        else:
            st.warning("Code input cannot be empty.")

    if st.button("Done", key="done_button"):
        if len(st.session_state.code_variants) >= 2:
            clear_voting_state()
            init_voting_round()
            next_page()
            st.rerun()
        else:
            st.warning("Please add at least two code variants before proceeding.")

    if os.path.exists("competitions/current_voting_state.json") and len(st.session_state.code_variants) == 0:
        if st.button("Continue", key="continue_voting_button"):
            load_voting_state()
            st.session_state.current_page = 'voting'
            st.rerun()

    if st.button("History", key="view_saved_competitions_button"):
        st.session_state.current_page = 'saved_competitions'
        st.rerun()


# Function to process a pair of variants
def process_pair(pair, index):
    variant_1, variant_2 = pair
    col1, col2 = st.columns(2)

    with col1:
        st.code(variant_1)
        if st.button("Select", key=f"select_1_{index}"):
            st.session_state.next_round_variants.append(variant_1)
            st.session_state.voting_results[variant_1] += 1
            st.session_state.current_pair_index += 1
            save_voting_state()
            if st.session_state.current_pair_index >= len(st.session_state.pairs):
                finalize_round()
            else:
                st.rerun()

    with col2:
        st.code(variant_2)
        if st.button("Select", key=f"select_2_{index}"):
            st.session_state.next_round_variants.append(variant_2)
            st.session_state.voting_results[variant_2] += 1
            st.session_state.current_pair_index += 1
            save_voting_state()
            if st.session_state.current_pair_index >= len(st.session_state.pairs):
                finalize_round()
            else:
                st.rerun()


# Move to the next pair or round
def advance_to_next_pair():
    st.session_state.current_pair_index += 1
    st.rerun()


# Finalize the round and check results
def finalize_round():
    max_votes = max(st.session_state.voting_results.values())
    potential_winners = [variant for variant, votes in st.session_state.voting_results.items() if votes == max_votes]

    if len(potential_winners) > 1 or len(st.session_state.remaining_variants) > 1:
        st.session_state.remaining_variants = potential_winners
        st.session_state.current_pair_index = 0
        st.session_state.next_round_variants = []
        st.session_state.current_round += 1
        st.session_state.pairs = []
        st.write(f"Several variants have the same number of votes. Proceeding to additional round {st.session_state.current_round} to determine the winner.")
        save_voting_state()
        st.rerun()
    else:
        st.session_state.remaining_variants = potential_winners
        save_competition_state()
        clear_voting_state()
        next_page()
        st.rerun()


# Main voting function
def voting():
    st.title(f"Voting (Round {st.session_state.current_round})")
    total_variants = len(st.session_state.remaining_variants)

    if total_variants == 1:
        next_page()
        st.rerun()
        return

    if total_variants % 2 == 1 and st.session_state.current_pair_index == 0:
        last_variant = st.session_state.remaining_variants.pop(-1)
        st.session_state.next_round_variants.append(last_variant)
        st.session_state.voting_results[last_variant] += 1

    if not st.session_state.pairs or st.session_state.current_pair_index == 0:
        st.session_state.pairs = [(st.session_state.remaining_variants[i], st.session_state.remaining_variants[i + 1])
                                  for i in range(0, len(st.session_state.remaining_variants), 2)]

    if st.session_state.current_pair_index < len(st.session_state.pairs):
        process_pair(st.session_state.pairs[st.session_state.current_pair_index], st.session_state.current_pair_index)
    else:
        finalize_round()


# Example function for showing results
def show_results():
    st.title("Winner")
    if st.session_state.remaining_variants:
        winner = st.session_state.remaining_variants[0]
        st.code(winner)

    sorted_results = sorted(st.session_state.voting_results.items(), key=lambda x: x[1], reverse=True)
    st.header("Previous Voting Results")
    st.table(sorted_results)

    if st.button("Save Competition"):
        save_competition_state()

    if st.button("History"):
        st.session_state.current_page = 'saved_competitions'
        st.rerun()

    if st.button("Restart"):
        st.session_state.clear()
        clear_voting_state()
        st.rerun()


# Main function to handle pages
def main():
    initialize_session_state()

    if st.session_state.current_page == 'add_code':
        add_code()
    elif st.session_state.current_page == 'voting':
        voting()
    elif st.session_state.current_page == 'results':
        show_results()
    elif st.session_state.current_page == 'saved_competitions':
        display_saved_competitions()


main()
