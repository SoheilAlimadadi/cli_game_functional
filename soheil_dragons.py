import os
import json
import time
import sys
from typing import (
    List,
    Dict
)
from helper.types import (
    GameMap,
    Coordinate
)
from random import (
    randint,
    choice
)
from math import dist
from tabulate import tabulate


def main() -> None:
    """The main function of the game that prepares and runs the game"""

# =====================Game Settings=======================

    # is used in menu and game to quit
    QUIT_BUTTON: str = 'q'
    # to back from instructions page to menu page
    BACK_BUTTON: str = 'b'
    # to show instructions page
    HELP: str = 'help'
    # how you will be shown on the map
    PLAYER: str = '😎'
    # clears terminal before menu shows up
    clear_terminal()
    # if needed the first time the game runs
    make_initial_database()
    # on this page user decides to register or login
    user_name: str = register_or_login()
    # menu before starting the game
    make_game_menu(PLAYER, HELP, QUIT_BUTTON, BACK_BUTTON, user_name)
    difficulty: str = choose_mode()
    # width of the map
    ROW_LEN: int = get_row() if difficulty == '4' else 17
    # height of the map
    COLUMN_LEN: int = get_col() if difficulty == '4' else 17
    # how dragon🐉 is shown on the map
    DRAGON: str = get_dragon() if difficulty == '4' else '⬜'
    # how dungeon door`🟥` is shown on the map
    DUNGEON_DOOR: str = get_door() if difficulty == '4' else '⬜'
    # number of dragons
    DRAGON_NUM: int = calculate_dragonnum(difficulty)
    # the range which you get smelled by dragon
    DRAGON_SMELLZONE: int = 5
    # number of healths the player has
    HEALTH_NUM: int = get_healthnum(difficulty)
    # How cells of the map are shown
    MAP_TILES: str = '⬜'
    # how walls of the map are shown
    MAP_WALLS: str = '⬛'
    # is dragon alerted by the player
    VISIBLE_DRAGON: str = '🐉'
    # initial canvas of the game
    game_map: GameMap = create_map(ROW_LEN, COLUMN_LEN, MAP_TILES, MAP_WALLS)
    # (x , y) coordinate of the dungeon door
    DUNGEON_DOOR_POS: Coordinate = get_dungeon_door_pos(
        MAP_WALLS,
        game_map,
        ROW_LEN,
        COLUMN_LEN
    )
    # place the dungeon door on map
    place_dungeon_door(game_map, DUNGEON_DOOR, DUNGEON_DOOR_POS)
    # (x , y) coordinate of the dragon
    dragons_pos: List[Coordinate] = get_dragon_pos(
        game_map,
        ROW_LEN,
        COLUMN_LEN,
        DUNGEON_DOOR_POS,
        DRAGON_NUM,
        MAP_WALLS
    )
    # place the dragon on map
    place_dragon(game_map, DRAGON, dragons_pos)
    UP: str = 'up'
    DOWN: str = 'down'
    LEFT: str = 'left'
    RIGHT: str = 'right'
    VALID_INPUTS: tuple[str] = (UP, DOWN, RIGHT, LEFT, QUIT_BUTTON)
    # is used to move the player based on inputs
    MOVEMENTS: Dict[str, Coordinate] = {
        UP: (0, -1),
        DOWN: (0, 1),
        RIGHT: (1, 0),
        LEFT: (-1, 0)
    }
    hearts: List[str] = ['💜' for _ in range(HEALTH_NUM)]
    player_info: Coordinate = (ROW_LEN // 2, COLUMN_LEN - 2)
    alt_movements: List[Coordinate] = list(MOVEMENTS.values())[:]
    alerted_dragons: List[Coordinate] = list()

# ==================Main loop of the game====================

    # main loop of the game
    while True:
        draw_player(game_map, player_info, PLAYER)
        draw_canvas(game_map)
        print_info(QUIT_BUTTON, MOVEMENTS, hearts, alerted_dragons)
        player_input: str = get_input(VALID_INPUTS)
        clear_terminal()
        if player_input == QUIT_BUTTON:
            clear_terminal()
            sys.exit()

        if not player_input:
            continue

        delete_player(game_map, player_info, MAP_TILES)
        player_info: Coordinate = calculate_new_position(
            game_map,
            player_input,
            MOVEMENTS,
            player_info,
            MAP_WALLS
        )

        alerted_dragons: List[Coordinate] = is_dragonsmellrange(
            dragons_pos,
            player_info,
            DRAGON_SMELLZONE,
        )

        if alerted_dragons:
            dragons_pos: List[Coordinate] = dragon_moves(
                MAP_WALLS,
                alt_movements,
                game_map,
                alerted_dragons,
                dragons_pos,
                player_info,
                MAP_TILES,
            )

        draw_dragons(
            game_map,
            dragons_pos,
            DRAGON,
            VISIBLE_DRAGON,
            player_info
        )

        check_win_lose(
            player_info,
            dragons_pos,
            DUNGEON_DOOR_POS,
            hearts,
            user_name
        )

# =======Functions that are called throughout the main function==========


def draw_player(
    game_map: GameMap,
    player_info: Coordinate,
    player: str,
) -> str:
    """draws the player on the map

    Parameters
    ----------
    game_map: list : map of the game

    player_info: tuple : player coords on the map

    player: str : how player is displayed


    Returns player
    -------

    """

    player_xpos, player_ypos = player_info
    game_map[player_ypos][player_xpos] = player

    return player


def draw_canvas(game_map: GameMap) -> GameMap:
    """draws the canvas which the game happens in

    Parameters
    ----------
    game_map: list : map of the game


    Returns game_map
    -------

    """
    for row in game_map:
        print("".join(row))

    return game_map


def print_info(
    quit_button: str,
    movements: Dict[str, Coordinate],
    hearts: str,
    alert: List[Coordinate]
) -> None:
    """Show the commands to user

    Parameters
    ----------
    quit_button: str : the key that quits the game

    movements: dict : the dict of movement actions

    hearts: str : how health is displayed

    alert: list : list of coords of the alerted dragons

    Returns None
    -------

    """
    print(f"Health: {' '.join(hearts)}")
    if alert:
        print("ALERT: Dragon is suspicious and might move towards you!")
    print(f"Enter {', '.join(list(movements.keys()))} to move")
    print(f"Enter '{quit_button}' to quit the game.")


def get_input(valid_inputs: tuple[str]) -> str:
    """Get input from user and check if it is valid

    Parameters
    ----------
    valid_inputs: tuple : a set of valid inputs


    Returns the player's input
    -------

    """
    player_input = input('Move: ').strip().lower()

    if player_input not in valid_inputs:
        player_input = None

    return player_input


def clear_terminal() -> None:
    """Clears the terminal"""
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')


def delete_player(
    game_map: GameMap,
    player_info: Coordinate,
    map_tile: str
) -> None:
    """Deletes the previous player sign from the map

    Parameters
    ----------
    game_map: list : map of the game

    player_info: tuple : players's coords on map

    map_tile: str : free cells on the map


    Returns None
    -------

    """
    player_xpos, player_ypos = player_info
    game_map[player_ypos][player_xpos] = map_tile


def calculate_new_position(
    game_map: GameMap,
    player_input: str,
    movements: Dict[str, Coordinate],
    player_info: Coordinate,
    map_walls: str
) -> None:
    """Calculates the new player position on the map based on user's input

    Parameters
    ----------
    game_map: list : map of the game

    player_input: str : player's input

    movements: dict : a set of movement actions

    player_info: tuple : player's coords

    map_walls: str : how walls of the map are shown


    Returns new player coords
    -------

    """
    # player_xpos and player_ypos are the current pos of player on the map
    player_xpos, player_ypos = player_info
    # movements[player_input] shows how much needs to be added or deducted
    # for example movements['up'] = (0, -1), deducting 1 from y
    x_movement, y_movement = movements[player_input]
    new_player_ypos = player_ypos + y_movement
    new_player_xpos = player_xpos + x_movement

    if game_map[new_player_ypos][new_player_xpos] == map_walls:
        # if hits the sides of the map stops
        new_player_xpos = player_xpos
        # if hits ceiling or floor doesn't move
        new_player_ypos = player_ypos
    return new_player_xpos, new_player_ypos


def is_dragonsmellrange(
    dragons_pos: List[Coordinate],
    player_pos: Coordinate,
    smell_zone: int,
) -> List[Coordinate]:
    """Calculates whether player is in smell range of the dragon

    Parameters
    ----------
    dragons_pos: list : dragons coords on the map

    player_pos: tuple : player's position on the map

    smell_zone: int : the distance which dargon can smell player


    Returns the coords of dragons that are alerted by the player
    -------

    """
    alerted_dragonpos = list()
    for dragon_pos in dragons_pos:
        if dist(player_pos, dragon_pos) <= smell_zone:
            alerted_dragonpos.append(dragon_pos)

    return alerted_dragonpos


def dragon_moves(
    map_walls: str,
    alt_movements: List[Coordinate],
    game_map: GameMap,
    alerted_dragonspos: List[Coordinate],
    dragons_pos: List[Coordinate],
    player_pos: Coordinate,
    map_tile: str,
) -> List[Coordinate]:
    """Calculates dragon's next move

    Parameters
    ----------
    map_walls: str : how walls of the map are displayed

    alt_movements: list : a list of tuples containing movements

    game_map: list : map of the game

    alerted_dragonspos: list : coords of dragons that have been alerted

    dragons_pos: list : current dragons coords

    player_pos: tuple : player's coords on the map

    map_tile: str : the free cells on the map


    Returns new dragons coords
    -------

    """
    thirty_chance = [1, 0, 0]
    sixty_chance = [1, 1, 0]
    for alerted_dragonpos in alerted_dragonspos:
        # unpacking the alerted dragon coord
        dragon_x, dragon_y = alerted_dragonpos

        # if dist is more than 2, ~30% chance to choose the best move
        if dist(alerted_dragonpos, player_pos) > 2:
            chance = choice(thirty_chance)
        # else ~60%
        else:
            chance = choice(sixty_chance)
        # if best move is chosen, calculate the best move with dist()
        if chance:
            # min([(dist_to_player, (x, y)), (dist_to_player, (x1, y1)), ...])
            shortest_move = min(
                [(dist(
                    (dragon_x + x_mov, dragon_y + y_mov), player_pos
                ), (x_mov, y_mov))for x_mov, y_mov in alt_movements]
            )
            maybe_shortest_move = shortest_move[1]
        # else choose a random movement
        else:
            maybe_shortest_move = choice(alt_movements)
        # Change this
        try:
            x_move, y_move = maybe_shortest_move
            new_dragon_x = dragon_x + x_move
            new_dragon_y = dragon_y + y_move
            if (game_map[new_dragon_y][new_dragon_x] == map_walls) or (
               (new_dragon_x, new_dragon_y) in dragons_pos):
                raise ValueError
        except (ValueError, IndexError):
            new_dragon_x = dragon_x
            new_dragon_y = dragon_y
        # removing the dragon from alerted dragons
        dragons_pos.remove(alerted_dragonpos)
        game_map[dragon_y][dragon_x] = map_tile
        # adding the dragon to new dragon coords
        dragons_pos.append((new_dragon_x, new_dragon_y))

    return dragons_pos


def draw_dragons(
    game_map: GameMap,
    dragons_pos: List[Coordinate],
    dragon: str,
    visible_dragon: str,
    player_pos: Coordinate
) -> str:
    """Updates the dragons on the map based on new coords

    Parameters
    ----------
    game_map: list : map of the game

    dragons_pos: list : coords of the dragons

    dragon: str : how dragon is displayed on the map normally

    visible_dragon: str : how dragon is displayed when it is visible

    player: str : how player is displayed

    player_pos: tuple : player's coords


    Returns dragon
    -------

    """

    for dragon_pos in dragons_pos:
        dragon_x, dragon_y = dragon_pos
        # dragon will become visible when it is close
        if dist(dragon_pos, player_pos) <= 3:
            game_map[dragon_y][dragon_x] = visible_dragon
        else:
            game_map[dragon_y][dragon_x] = dragon

    return dragon


def check_win_lose(
    player_info: Coordinate,
    dragons_pos: List[Coordinate],
    dungeon_door_pos: Coordinate,
    hearts: List[str],
    user_name: str
) -> None:
    """Check if the player wins or loses the game

    Parameters
    ----------
    player_info: tuple : player's coords on the map

    dragons_pos: list : dragons coords on the map

    dungeon_door_pos: tuple : the coords on the dungeon door

    hearts: list :  the health bar of the player

    user_name: str : the username of the player


    Returns None
    -------

    """
    game_state = 'ongoing'
    for dragon_pos in dragons_pos:
        if dist(player_info, dragon_pos) <= 1:
            hearts.pop()

        if dragon_pos == player_info or not hearts:
            game_state = 'loss'
            update_database(user_name, game_state)
            lose_game(user_name)

    if player_info == dungeon_door_pos:
        game_state = 'win'
        update_database(user_name, game_state)
        win_game(user_name)


def update_database(user_name: str, result: str) -> None:
    """Updating the games's database based on the result of the game

    Parameters
    ----------
    user_name:str : the player's username

    result: str : result of the game


    Returns None
    -------

    """
    with open('database.json') as data_base:
        contents = json.load(data_base)

    if result == 'win':
        contents['players'][user_name]['games won'] += 1
    else:
        contents['players'][user_name]['games lost'] += 1

    games_won = contents['players'][user_name]['games won']
    games_lost = contents['players'][user_name]['games lost']

    win_ratio = (games_won / (games_won + games_lost)) * 100
    contents['players'][user_name]['win ratio'] = win_ratio

    with open('database.json', 'w') as data_base:
        json_contents = json.dumps(contents, indent=4)
        data_base.write(json_contents)


def lose_game(user_name: str) -> None:
    """Show lose message

    Parameters
    ----------
    user_name: str : player's user name


    Returns None
    -------

    """
    msg = """
    SORRY {}, YOU LOST :(
          """.format(user_name)
    print(msg)
    after_game()


def win_game(user_name: str) -> None:
    """Show win message

    Parameters
    ----------
    user_name: str : player's username


    Returns None
    -------

    """
    msg = """
    YAY {}! YOU WON :)
          """.format(user_name)
    print(msg)
    after_game()


def after_game() -> None:
    """After win or lose waits 1 second and exits after clearing terminal"""
    time.sleep(1)
    clear_terminal()
    sys.exit()


def create_map(
    row_len: int,
    column_len: int,
    map_tiles: str,
    map_walls: str
) -> GameMap:
    """Create the initial map of the game

    Parameters
    ----------
    row_len: int : width of the map

    column_len: int : height of the map

    map_tiles: str : free cells on the map

    map_walls: str : walls of the map


    Returns game_map
    -------

    """
    # Game map
    game_map = [map_walls * row_len if col == 0 or col == (column_len - 1)
                else [map_walls if row == 0 or row == (row_len - 1)
                else map_tiles for row in range(row_len)]
                for col in range(column_len)]

    # The plus like in middle of the map, made with walls
    for index, _ in enumerate(game_map[row_len // 2]):
        if 3 <= index < row_len - 3:
            game_map[row_len // 2][index] = '⬛'

    for index, _ in enumerate(game_map):
        if 3 <= index < column_len - 3:
            game_map[index][(column_len - 1) // 2] = '⬛'

    return game_map


def get_dungeon_door_pos(
    map_walls: str,
    game_map: GameMap,
    row_len: int,
    column_len: int
) -> Coordinate:
    """Chooses where dungeon door position will be in map randomly

    Parameters
    ----------
    map_walls: str : walls of the map

    game_map: list : map of the game

    row_len: int : width of the map

    column_len: int : height of the map


    Returns dungeon's door coordinates
    -------

    """
    while True:
        # Dungeon door's horizontal position
        dungeon_door_xpos = randint(1, row_len - 2)
        # Dungeon door's vertical position
        dungeon_door_ypos = randint(1, column_len - (column_len // 3 + 2))

        if game_map[dungeon_door_ypos][dungeon_door_xpos] == map_walls:
            continue
        break

    return dungeon_door_xpos, dungeon_door_ypos


def place_dungeon_door(
    game_map: GameMap,
    dungeon_door: str,
    dungeon_door_pos: Coordinate,
) -> GameMap:
    """Place the Dungeon Door on the map

    Parameters
    ----------
    game_map: list : map of the game

    dungeon_door: str : how dungeon's exit door is displayed

    dungeon_door_pos: tuple : coords of the dungeon door on the map


    Returns game_map
    -------

    """
    dungeon_door_x, dungeon_door_y = dungeon_door_pos
    game_map[dungeon_door_y][dungeon_door_x] = dungeon_door

    return game_map


def get_dragon_pos(
    game_map: GameMap,
    row_len: int,
    column_len: int,
    dungeon_door_pos: Coordinate,
    dragon_num: int,
    map_wall: str
) -> List[Coordinate]:
    """Chooses where dragons position will be in map randomly

    Parameters
    ----------
    game_map: list : map of the game

    row_len: int : width of the map

    column_len: int : height of the map

    dungeon_door_pos: tuple : the coords of the dungeon door

    dragon_num: int : the number of dragons on the map

    map_wall: str : how walls are displayed on the map


    Returns list of dragon coords on the map
    -------

    """
    dragonpos_list = list()
    for _ in range(dragon_num):
        while True:
            # dragon's horizontal position
            dragon_xpos = randint(2, row_len - 2)
            # dragon's vertical position
            dragon_ypos = randint(2, column_len - (column_len // 3))
            if (dragon_xpos, dragon_ypos) == dungeon_door_pos:
                continue
            if game_map[dragon_ypos][dragon_xpos] == map_wall:
                continue

            dragonpos_list.append((dragon_xpos, dragon_ypos))

            break

    return dragonpos_list


def place_dragon(
    game_map: GameMap,
    dragon: str,
    dragons_pos: List[Coordinate]
) -> str:
    """Makes the Dragon visible on the map if needed for test

    Parameters
    ----------
    game_map: list : map of the game

    dragon: str : how dragon is displayed on the map

    dragons_pos: list : coords of the dragons


    Returns dragon
    -------

    """
    for dragon_pos in dragons_pos:
        dragon_xpos, dragon_ypos = dragon_pos
        game_map[dragon_ypos][dragon_xpos] = dragon

    return dragon


def register_or_login() -> str:
    """A menu page which user decides to login or register in"""
    clear_terminal()
    while True:
        user_name = None
        print_logo()
        print("Enter 'R' to register")
        print_separator()
        print("Press RETURN to login")
        print_separator()
        print("Enter 'L' to see the leaderboards")
        print_separator()
        print("Enter 'Q' to exit the game\n")
        user_input = input().strip().lower()
        clear_terminal()
        if not user_input:
            user_name = login()

        if user_input == 'r':
            user_name = register()

        if user_input == 'l':
            show_leaderboard()
            clear_terminal()

        if user_input == 'q':
            clear_terminal()
            sys.exit()

        if not user_name:
            continue

        else:
            break

    return user_name


def make_initial_database() -> None:
    """Creates the database file if it isn't created yet"""
    if 'database.json' not in os.listdir():
        data_dict = dict()
        with open('database.json', 'w') as data_base:
            data_dict.setdefault('players', dict())
            jason_database = json.dumps(data_dict, indent=4)
            data_base.write(jason_database)


def register() -> str:
    """Registers the username and password of the game to the database"""
    while True:
        with open('database.json', 'r') as data_base:
            contents = json.load(data_base)
        print_logo()
        user_name = input("Username: ").strip().lower()
        if user_name in contents['players']:
            print(f"{user_name} already exists, choose another one.")
            time.sleep(1)
            clear_terminal()
            continue
        clear_terminal()
        print_logo()
        password = input("Password: ")
        repeat_pass = input("Repeat password: ")

        clear_terminal()
        if not repeat_pass == password:
            print('Passwords do not match, try again!')
            time.sleep(1)
            clear_terminal()
            continue
        break

    with open('database.json', 'w') as data_base:
        contents['players'][user_name] = dict()
        contents['players'][user_name]['password'] = password
        contents['players'][user_name]['games won'] = 0
        contents['players'][user_name]['games lost'] = 0
        contents['players'][user_name]['win ratio'] = 0

        player_data = json.dumps(contents, indent=4)
        data_base.write(player_data)

    print_logo()
    print(f'{user_name} registered successfully!')
    time.sleep(1)
    clear_terminal()
    return user_name


def login() -> str:
    """Logs in the user to the game"""
    data_base = open('database.json')
    contents = json.load(data_base)
    while True:
        print_logo()
        user_name = input("Username: ")
        clear_terminal()
        if user_name not in contents['players']:
            print_logo()
            print(f"'{user_name}' not found, press RETURN try again!")
            print("Or enter any key to go back to the first page")
            usr_inp = input()
            clear_terminal()
            if not usr_inp:
                continue
            user_name = None
            break
        print_logo()
        password = input("Password: ")
        clear_terminal()
        if not contents['players'][user_name]['password'] == password:
            user_name = None
            print("Wrong password")
            print('~~~~~~~~~~~~~~~')
            print('Press RETURN to try again')
            print("Enter any key to go back")
            user_input = input().strip().lower()
            clear_terminal()

            if not user_input:
                continue
        break

    data_base.close()
    return user_name


def make_game_menu(
    player: str,
    help: str,
    quit_button: str,
    back_button: str,
    user_name: str
) -> None:
    """Prepares the game before the main game loop

    Parameters
    ----------
    player: str : how player is displayed

    help: str : the valid string for help

    quit_button: str : the valid string for quitting

    back_button: str : the valid string for back

    user_name: str : username of the player


    Returns None
    -------

    """
    while True:
        print_logo()
        print(f"Welcome {user_name}\n")
        print('Press RETURN to start the game')
        print(f"Enter '{help}' to see game instructions")
        print(f"Enter {quit_button} to quit the game.")
        user_input = input().strip().lower()
        clear_terminal()
        # to quit the game
        if user_input == quit_button:
            sys.exit()
        # to start the game
        elif not user_input:
            pass
        # to show instructions page
        elif user_input == help:
            show_instructions(
                player, help, quit_button, back_button, user_name
            )
        # invalid inputs
        else:
            continue

        break


def choose_mode() -> str:
    """Difficulty mode of the game is chosen"""
    valid_inputs = ['1', '2', '3', '4']
    while True:
        print_logo()
        print("Choose one of the following modes:")
        print("1. Easy, 2. Normal, 3. Hard, 4. Test mode")
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        user_input = input("Enter 1, 2, 3 or 4: ")
        clear_terminal()

        if user_input not in valid_inputs:
            print('Not a valid input')
            continue
        break

    return user_input


def get_row() -> int:
    """Asks the user for the width of the map"""
    msg = "Width of the map: "
    print_logo()
    return get_intput(msg)


def get_col() -> int:
    """Asks the user for the height of the map"""
    msg = "Height of the map: "
    return get_intput(msg)


def get_dragon() -> str:
    """Asks the user for how dragons will be displayer"""
    dragon = input("Enter how dragon will be displayed (only emoji 🐉): ")
    return dragon


def get_door() -> str:
    """Asks the user for how dungeon door will be displayed"""
    door = input("Enter how dungeon door will be displayed (only emoji 🟥): ")
    return door


def calculate_smellzone(diff: str) -> int:
    """Calculates the size of the smellzone based on the difficulty

    Parameters
    ----------
    diff: str : game's difficulty


    Returns size of the smellzone
    -------

    """
    msg = "Enter the distance that dragon smells the player: "
    if diff == '1':
        smellzone = 3
    elif diff == '2':
        smellzone = 5
    elif diff == '3':
        smellzone = 7
    else:
        smellzone = get_input(msg)

    return smellzone


def calculate_dragonnum(diff: str) -> int:
    """Calculates the number of dragons based on difficulty

    Parameters
    ----------
    diff: str : difficulty of the game


    Returns number of dragons
    -------

    """
    msg = "Enter the number of dragons on the map: "
    if diff == '1':
        dragon_num = 2
    elif diff == '2':
        dragon_num = 3
    elif diff == '3':
        dragon_num = 4
    else:
        dragon_num = get_intput(msg)

    return dragon_num


def get_intput(msg: str) -> int:
    """Asks for a integer input from the player

    Parameters
    ----------
    msg: str : message printed on the terminal while asking for input


    Returns player's input
    -------

    """
    while True:
        try:
            user_input = int(input(msg))
        except ValueError:
            print("Input must be integer!")
            time.sleep(1)
            continue
        break
    return user_input


def get_healthnum(diff: str) -> int:
    """Calculates the number of healths based on the difficulty

    Parameters
    ----------
    diff:str : difficulty of the game


    Returns health bar
    -------

    """
    msg = "Enter number of healths the player has: "
    if diff == '1':
        health = 4
    elif diff == '2':
        health = 3
    elif diff == '3':
        health = 4
    else:
        health = get_intput(msg)

    clear_terminal()
    return health


def show_leaderboard() -> None:
    """Prints a table in the terminal containing the game's leaderboard"""
    with open('database.json') as data_base:
        contents = json.load(data_base)

    players_stats = list()
    for name, stats in contents['players'].items():
        player = dict()
        player.setdefault('Name', name)
        for stat, value in stats.items():
            if stat == 'games won':
                player.setdefault('Games won', value)
            if stat == 'games lost':
                player.setdefault('Games lost', value)
            if stat == 'win ratio':
                player.setdefault('Win ratio', value)
        players_stats.append(player)

    sorted_players = sorted(
        players_stats, key=lambda player: player['Win ratio']
    )
    sorted_players = [
        {
            stat: (
                f"{value:.2f} %" if stat == 'Win ratio' else value
            ) for stat, value in player.items()
        } for player in sorted_players
    ]

    if not len(sorted_players):
        print("No registered users yet")
    else:
        headers = list(sorted_players[0].keys())
        rows = [player.values() for player in sorted_players]
        print(tabulate(rows, headers, tablefmt='grid'))
    print('\n\nPress RETURN to go back.')
    input()

    return None


def show_instructions(
    player: str,
    help: str,
    quit_button: str,
    back_button: str,
    user_name: str
) -> None:
    """Shows the instructions of the game

    Parameters
    ----------
    player: str : how player is displayed

    help: str : valid input for help

    quit_button: str : valid input for quit

    back_button: str : valid input for back

    user_name: str : player's username

    Returns None
    -------

    """
    while True:
        print(
            """
*******************************************************
Welcome to Dungeon & Dragons
-------------------------------------------------------
You  are   shown  on   the   map   with  the  sign  '{}'
You can move by typing 'up', 'down', 'left' and 'right'
The only escape route out of the dungeon is through the
dungeon door which is not displayed on the map.
But there are hidden dragons on the map & you will die
if you collide with it.
------------------------------------------------------
Enter '{}' to go back to the menu ...
*******************************************************
            """.format(player, back_button)
        )
        # back to menu
        if input() == back_button:
            clear_terminal()
            make_game_menu(player, help, quit_button, back_button, user_name)
            break
        # invalid input
        else:
            clear_terminal()
            continue


def print_separator() -> None:
    """Prints line separator"""
    print('~~~' * 11)


def print_logo() -> None:
    """Prints game's logo"""
    print(
            """
*********************************
*********** Dungeon *************
************** & ****************
*********** Dragons *************
*********************************
            """)


if __name__ == '__main__':
    main()
