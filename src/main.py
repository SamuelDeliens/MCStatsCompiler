import configparser
import sqlite3
from stats_compiler import load_vanilla_data, load_cobblemon_data, get_vanilla_leaderboard, get_vanilla_best_and_worst, \
    process_cobblemon_leaderboards
from excel_to_image import generate_leaderboard_image


def init_database(db_path="scoreboard.db"):
    """Initialize or connect to the SQLite database for leaderboards"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table creation for leaderboards
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS standard_leaderboard (
            rank INTEGER,
            player_name TEXT,
            score INTEGER,
            last_updated TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shiny_leaderboard (
            rank INTEGER,
            player_name TEXT,
            score INTEGER,
            last_updated TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS legendary_leaderboard (
            rank INTEGER,
            player_name TEXT,
            score INTEGER,
            last_updated TEXT
        )
    ''')
    conn.commit()
    return conn


def main():
    # Read config
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf8')

    # Only support manual and local modes after removing FTP
    if config['INPUT']['Mode'] not in ['manual', 'local']:
        raise Exception(
            "Invalid input mode: " + config['INPUT']['Mode'] + ". Only 'manual' and 'local' modes are supported.")

    # Database initialization if needed
    conn = None
    if config['COBBLEMONLEADERBOARDS']['SQLiteOutput'] == "true":
        conn = init_database("scoreboard.db")

    # Process Vanilla data
    vanilla_df = None
    if config['VANILLALEADERBOARD']['Enable'] == "true" or config['BESTANDWORST']['Enable'] == "true":
        print("LOADING VANILLA DATA")
        vanilla_df = load_vanilla_data(
            config['VANILLALEADERBOARD']['CreateCSV'],
            config['VANILLALEADERBOARD']['CSVPath'],
            config['INPUT']['Mode'],
            config['INPUT']['LocalPath']
        )

    # Process Cobblemon data
    cobblemon_df = None
    if config['COBBLEMONLEADERBOARDS']['TotalEnable'] == "true" or config['COBBLEMONLEADERBOARDS'][
        'ShinyEnable'] == "true" or config['COBBLEMONLEADERBOARDS']['LegEnable'] == "true":
        print("LOADING COBBLEMON DATA")
        if config['GLOBALMATRIX']['UseCSV'] == "false":
            cobblemon_df = load_cobblemon_data(
                config['GLOBALMATRIX']['CreateCSV'],
                config['GLOBALMATRIX']['CSVPath'],
                config['INPUT']['Mode'],
                config['INPUT']['LocalPath']
            )
        else:
            import pandas as pd
            cobblemon_df = pd.read_csv(config['GLOBALMATRIX']['CSVPath'], index_col=[0, 1, 2], skipinitialspace=True)

    # First leaderboard testing
    if config['VANILLALEADERBOARD']['Enable'] == "true" and vanilla_df is not None:
        get_vanilla_leaderboard(
            vanilla_df,
            config['VANILLALEADERBOARD']['Category'],
            config['VANILLALEADERBOARD']['Subcategory']
        )

    # First bestandworst testing
    if config['BESTANDWORST']['Enable'] == "true" and vanilla_df is not None:
        get_vanilla_best_and_worst(
            vanilla_df,
            config['BESTANDWORST']['Username'],
            config['BESTANDWORST']['Cleaning'],
            config['BESTANDWORST']['CleaningValue']
        )

    # Process Cobblemon leaderboards
    if cobblemon_df is not None:
        process_cobblemon_leaderboards(cobblemon_df, config, conn)

    # Generate images from Excel for each enabled leaderboard
    if config['COBBLEMONLEADERBOARDS']['TotalEnable'] == "true":
        generate_leaderboard_image("leaderboard2", "classement_pokemon_total.png", "Qui a attrapé le plus de Pokémon ?")

    if config['COBBLEMONLEADERBOARDS']['ShinyEnable'] == "true":
        generate_leaderboard_image("leaderboard3", "classement_pokemon_shiny.png",
                                   "Qui a attrapé le plus de Pokémon Shiny ?")

    if config['COBBLEMONLEADERBOARDS']['LegEnable'] == "true":
        generate_leaderboard_image("leaderboard4", "classement_pokemon_legendaire.png",
                                   "Qui a attrapé le plus de Pokémon Légendaires ?")

    # Close SQLite connection
    if conn:
        conn.close()

    print("Done!")


if __name__ == "__main__":
    main()