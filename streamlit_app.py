import streamlit as st
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

# Navigate to the next page
def next_page():
    page_flow = {
        'add_code': 'voting',
        'voting': 'results',
    }
    st.session_state.current_page = page_flow.get(st.session_state.current_page, 'results')

# Initialize the voting round
def init_voting_round():
    st.session_state.remaining_variants = st.session_state.code_variants.copy()
    st.session_state.current_round = 1
    st.session_state.voting_results.clear()
    st.session_state.current_pair_index = 0
    st.session_state.next_round_variants = []

# Handle code addition
def add_code():
    st.title("Add Your Code")
    code_input = st.text_area("Your Code", value="")

    if st.button("Add"):
        if code_input.strip():
            st.session_state.code_variants.append(code_input)
            st.success("Code variant added.")
        else:
            st.warning("Code input cannot be empty.")

    if st.button("Done"):
        if len(st.session_state.code_variants) >= 2:
            init_voting_round()
            next_page()
            st.rerun()
        else:
            st.warning("Please add at least two code variants before proceeding.")

# Function to process a pair of variants
def process_pair(pair, index):
    variant_1, variant_2 = pair
    col1, col2 = st.columns(2)

    with col1:
        st.code(variant_1)
        if st.button("Select", key=f"select_1_{index}"):
            st.session_state.next_round_variants.append(variant_1)
            st.session_state.voting_results[variant_1] += 1
            if st.session_state.current_pair_index >= len(st.session_state.pairs) - 1:
                finalize_round()
            else:
                advance_to_next_pair()

    with col2:
        st.code(variant_2)
        if st.button("Select", key=f"select_2_{index}"):
            st.session_state.next_round_variants.append(variant_2)
            st.session_state.voting_results[variant_2] += 1
            if st.session_state.current_pair_index >= len(st.session_state.pairs) - 1:
                finalize_round()
            else:
                advance_to_next_pair()

# Move to the next pair or round
def advance_to_next_pair():
    st.session_state.current_pair_index += 1
    st.rerun()

# Finalize the round and check results
def finalize_round():
    max_votes = max(st.session_state.voting_results.values())
    potential_winners = [variant for variant, votes in st.session_state.voting_results.items() if votes == max_votes]

    # If more than one variant remains or all variants have equal votes
    if len(potential_winners) > 1 or len(st.session_state.remaining_variants) > 1:
        # Move variants to the next voting round
        st.session_state.remaining_variants = potential_winners
        st.session_state.current_pair_index = 0
        st.session_state.next_round_variants = []
        st.session_state.current_round += 1
        st.write(f"Several variants have the same number of votes. Proceeding to additional round {st.session_state.current_round} to determine the winner.")
        st.rerun()
    else:
        # If only one variant remains, finish voting and proceed to results
        st.session_state.remaining_variants = potential_winners
        next_page()
        st.rerun()


# Main voting function
def voting():
    st.title(f"Voting (Round {st.session_state.current_round})")
    total_variants = len(st.session_state.remaining_variants)

    # Finish if only one variant remains
    if total_variants == 1:
        next_page()
        st.rerun()
        return

    # Automatically advance the last variant in case of an odd number of variants
    if total_variants % 2 == 1 and st.session_state.current_pair_index == 0:
        last_variant = st.session_state.remaining_variants.pop(-1)
        st.session_state.next_round_variants.append(last_variant)
        st.session_state.voting_results[last_variant] += 1

    # Form pairs for comparison
    st.session_state.pairs = [(st.session_state.remaining_variants[i], st.session_state.remaining_variants[i + 1])
                              for i in range(0, len(st.session_state.remaining_variants), 2)]

    # Display the current pair for voting
    if st.session_state.current_pair_index < len(st.session_state.pairs):
        process_pair(st.session_state.pairs[st.session_state.current_pair_index], st.session_state.current_pair_index)

# Function to display results
def show_results():
    st.title("Winner")

    if st.session_state.remaining_variants:
        winner = st.session_state.remaining_variants[0]
        st.code(winner)

    # Sort results by number of votes in descending order
    sorted_results = sorted(st.session_state.voting_results.items(), key=lambda x: x[1], reverse=True)

    st.header("Previous Voting Results")
    st.table(sorted_results)

    if st.button("Restart"):
        st.session_state.clear()
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

# Call the main function
main()
