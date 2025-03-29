import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.table import Table


def generate_leaderboard_image(sheet_name="leaderboard2", output_file="classement_pokemon.png", custom_title=None):
    """
    Generate an image from the Excel leaderboard

    Args:
        sheet_name: Name of the Excel sheet to use
        output_file: Output filename for the image
        custom_title: Custom title to display at the top of the image
    """
    print(f"Generating image for {sheet_name} as {output_file} with title '{custom_title}'...")
    # Read the Excel file
    df = pd.read_excel("output.xlsx", sheet_name=sheet_name, header=None)
    df = df.dropna(how='all')

    # Extract title and date info
    title = df.iloc[0, 1]
    date_str = df.iloc[-1, 1]

    # Extract player data
    players = []  # [rank, player, score]
    col_name = ["Rank", "Player", "Score"]

    for i in range(1, len(df)):
        if (not pd.isna(df.iloc[i, 1]) and
                not pd.isna(df.iloc[i, 2]) and
                not pd.isna(df.iloc[i, 3])):
            players.append([
                df.iloc[i, 1],
                df.iloc[i, 2],
                int(df.iloc[i, 3])
            ])

    # We don't need to sort as the data is already sorted in the Excel file
    # This line is commented out to preserve the rank numbers from Excel
    # players = sorted(players, key=lambda x: x[2], reverse=True)

    # Create figure
    fig_height = max(4, len(players) * 0.4)
    plt.figure(figsize=(10, fig_height), facecolor='#131e33')
    ax = plt.gca()
    plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.05)
    ax.axis('off')
    ax.axis('tight')

    # Prepare row colors - based on ranking position
    colors = []
    for player in players:
        # Extract rank position (could be "1.", "2.", etc.)
        try:
            rank_position = int(player[0].replace(".", ""))
        except (ValueError, TypeError):
            rank_position = 99  # Default high value if parsing fails

        if rank_position == 1:  # 1st - Gold
            row_color = ['#FFD700'] * 3
        elif rank_position == 2:  # 2nd - Silver
            row_color = ['#C0C0C0'] * 3
        elif rank_position == 3:  # 3rd - Bronze
            row_color = ['#CD7F32'] * 3
        else:  # Others - Light background
            row_color = ['#f5f5f5'] * 3
        colors.append(row_color)

    # Create table
    table = ax.table(
        cellText=players,
        colLabels=col_name,
        cellLoc='center',
        loc='center',
        cellColours=colors,
        colWidths=[0.1, 0.5, 0.3]
    )

    # Customize table
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2)

    # Cell styling
    for (i, j), cell in table.get_celld().items():
        if i == 0:  # Header
            cell.set_text_props(fontweight='bold', color='white')
            cell.set_facecolor('#2a75bb')  # Pokémon blue
        if j == 2:  # Score column
            cell.get_text().set_horizontalalignment('right')

    # Main title
    display_title = custom_title if custom_title else 'Qui a attrapé le plus de Pokémon ?'
    title = ax.text(
        0.5, 0.95, display_title,
        transform=ax.transAxes,
        ha='center', va='bottom',
        fontsize=18, fontweight='bold',
        color='#95BADD'  # Pokémon blue
    )

    # Date text
    ax.text(
        0.5, 0.02,
        date_str,
        transform=ax.transAxes,
        ha='center',
        va='bottom',
        fontsize=10,
        color='#666666'
    )

    # Save the image
    plt.tight_layout()
    plt.savefig(
        "./images/" + output_file,
        bbox_inches='tight',
        dpi=150,
        transparent=False
    )

    print(f"Leaderboard image saved as {output_file}")