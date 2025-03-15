import asyncio
import random
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, deque
from datetime import datetime

async def roll_dice(sides: int, dice_id: int = 0) -> tuple:
    """
    Simulate rolling a die with a given number of sides.
    
    Args:
        sides: Number of sides on the die
        dice_id: Identifier for the specific die
        
    Returns:
        Tuple of (dice_id, result)
    """
    await asyncio.sleep(0.01 * random.random())  # Simulate varying roll times
    result = random.randint(1, sides)
    return (dice_id, result)

async def roll_multiple_dice(num_dice: int, sides: int) -> list:
    """
    Roll multiple dice concurrently.
    
    Args:
        num_dice: Number of dice to roll
        sides: Number of sides per die
        
    Returns:
        List of roll results
    """
    tasks = [roll_dice(sides, i) for i in range(num_dice)]
    results = await asyncio.gather(*tasks)
    return results

def draw_dice(value: int, sides: int, size: int = 100) -> str:
    """
    Return an ASCII or Unicode representation of a die.
    
    Args:
        value: The value shown on the die
        sides: Number of sides on the die
        size: Size of the die visualization
        
    Returns:
        String representation of the die
    """
    if sides == 6:
        # Special representation for 6-sided dice
        dice_symbols = {
            1: "⚀",
            2: "⚁",
            3: "⚂",
            4: "⚃",
            5: "⚄",
            6: "⚅"
        }
        return f"<div style='font-size:{size}px;'>{dice_symbols.get(value, str(value))}</div>"
    else:
        # Generic representation for other dice
        return f"""
        <div style='
            width: {size}px;
            height: {size}px;
            line-height: {size}px;
            text-align: center;
            font-size: {size//2}px;
            font-weight: bold;
            border: 2px solid black;
            border-radius: {10 if sides == 6 else size//2}px;
            display: inline-block;
            margin: 5px;
            box-shadow: 3px 3px 5px #888888;
        '>
            {value}
        </div>
        """

def calculate_statistics(roll_history, sides):
    """Calculate statistics based on roll history."""
    if not roll_history:
        return {}
    
    all_rolls = [roll for sublist in roll_history for roll in sublist]
    
    stats = {
        "Total Rolls": len(all_rolls),
        "Average": round(sum(all_rolls) / len(all_rolls), 2),
        "Highest": max(all_rolls),
        "Lowest": min(all_rolls),
        "Most Common": Counter(all_rolls).most_common(1)[0][0],
    }
    
    return stats

def main():
    """Main Streamlit app function."""
    st.set_page_config(page_title="Dice Simulator", layout="wide")
    
    # Initialize session state
    if 'roll_history' not in st.session_state:
        st.session_state.roll_history = deque(maxlen=10)  # Store last 10 rolls
    if 'roll_timestamps' not in st.session_state:
        st.session_state.roll_timestamps = deque(maxlen=10)  # Store timestamps
    if 'total_rolls' not in st.session_state:
        st.session_state.total_rolls = 0
    
    # App title and description
    st.title("🎲 Dice Rolling Simulator")
    st.markdown("""
    Simulate rolling dice with different numbers of sides. The simulator uses asyncio 
    for concurrent dice rolling, providing realistic randomness and visualizations.
    """)
    
    # Sidebar controls
    st.sidebar.header("📊 Simulation Settings")
    
    num_dice = st.sidebar.number_input(
        "Number of Dice", min_value=1, max_value=20, value=2
    )
    sides = st.sidebar.selectbox(
        "Number of Sides per Die", 
        options=[4, 6, 8, 10, 12, 20, 100], 
        index=1,  # Default to 6-sided dice
        help="Select the type of dice (d4, d6, d8, etc.)"
    )
    
    # Advanced options
    with st.sidebar.expander("🛠️ Advanced Options"):
        show_stats = st.checkbox("Show Statistics", value=True)
        show_history = st.checkbox("Show Roll History", value=True)
        show_distribution = st.checkbox("Show Distribution", value=True)
    
    # Roll button with animation state
    roll_col, clear_col = st.sidebar.columns(2)
    roll_pressed = roll_col.button("🎲 Roll Dice", use_container_width=True)
    clear_pressed = clear_col.button("🗑️ Clear History", use_container_width=True)
    
    # Main content area
    if roll_pressed:
        with st.spinner(f"Rolling {num_dice} d{sides}..."):
            # Run async dice rolling and get results
            results = asyncio.run(roll_multiple_dice(num_dice, sides))
            dice_ids, roll_values = zip(*results)
            
            # Update session state
            st.session_state.roll_history.append(roll_values)
            st.session_state.roll_timestamps.append(datetime.now().strftime("%H:%M:%S"))
            st.session_state.total_rolls += 1
    
    if clear_pressed:
        st.session_state.roll_history.clear()
        st.session_state.roll_timestamps.clear()
        st.session_state.total_rolls = 0
    
    # Display latest roll results if available
    if st.session_state.roll_history:
        latest_roll = st.session_state.roll_history[-1]
        
        st.subheader("🎯 Latest Roll Results")
        
        # Display dice visually
        dice_html = ""
        for value in latest_roll:
            dice_html += draw_dice(value, sides)
        
        dice_container = st.container()
        dice_container.markdown(f"""
        <div style='display: flex; flex-wrap: wrap; gap: 10px;'>
            {dice_html}
        </div>
        """, unsafe_allow_html=True)
        
        # Display numerical results
        col1, col2 = st.columns(2)
        col1.markdown(f"**Individual Values:** {', '.join(map(str, latest_roll))}")
        col2.markdown(f"**Total:** **{sum(latest_roll)}**")
        
        # Two-column layout for stats and history
        if show_stats or show_history or show_distribution:
            stats_col, history_col = st.columns([1, 1])
            
            # Statistics
            if show_stats:
                with stats_col:
                    st.subheader("📈 Roll Statistics")
                    stats = calculate_statistics([item for item in st.session_state.roll_history], sides)
                    
                    st.markdown(f"""
                    - **Total Roll Sessions:** {st.session_state.total_rolls}
                    - **Total Dice Rolled:** {stats.get('Total Rolls', 0)}
                    - **Average Value:** {stats.get('Average', 0)}
                    - **Highest Value:** {stats.get('Highest', 0)}
                    - **Lowest Value:** {stats.get('Lowest', 0)}
                    - **Most Common Value:** {stats.get('Most Common', 'N/A')}
                    """)
                    
                    # Distribution visualization
                    if show_distribution and len(st.session_state.roll_history) > 0:
                        st.subheader("Distribution")
                        
                        all_rolls = [roll for sublist in st.session_state.roll_history for roll in sublist]
                        
                        fig, ax = plt.subplots()
                        counts = Counter(all_rolls)
                        x = list(range(1, sides + 1))
                        y = [counts.get(i, 0) for i in x]
                        
                        ax.bar(x, y, color='skyblue')
                        ax.set_xlabel('Dice Value')
                        ax.set_ylabel('Frequency')
                        ax.set_xticks(x)
                        
                        st.pyplot(fig)
            
            # Roll history
            if show_history:
                with history_col:
                    st.subheader("📜 Roll History")
                    
                    if st.session_state.roll_history:
                        history_data = []
                        for i, (timestamp, roll) in enumerate(zip(
                            st.session_state.roll_timestamps, 
                            st.session_state.roll_history
                        )):
                            history_data.append({
                                "Roll #": len(st.session_state.roll_timestamps) - i,
                                "Time": timestamp,
                                "Values": ", ".join(map(str, roll)),
                                "Total": sum(roll)
                            })
                        
                        history_df = pd.DataFrame(history_data)
                        st.dataframe(history_df, use_container_width=True)
                    else:
                        st.info("No roll history yet. Roll some dice!")

    else:
        # Initial state
        st.info("👆 Click 'Roll Dice' to begin rolling!")
        
        # Add explanations about dice notation
        with st.expander("ℹ️ About Dice Notation"):
            st.markdown("""
            ### Understanding Dice Notation
            
            In tabletop gaming, dice notation typically follows the format `NdS`, where:
            - `N` = Number of dice
            - `d` = Short for "dice"
            - `S` = Number of sides per die
            
            Common dice types include:
            - d4: Tetrahedron (4 faces)
            - d6: Regular cube (6 faces) - standard die
            - d8: Octahedron (8 faces)
            - d10: Pentagonal trapezohedron (10 faces)
            - d12: Dodecahedron (12 faces)
            - d20: Icosahedron (20 faces)
            - d100/Percentile: Often rolled using two d10s (one for tens, one for units)
            """)

if __name__ == "__main__":
    main()