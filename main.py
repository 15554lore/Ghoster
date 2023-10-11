import random
import logging
import os

from datetime import datetime
from tkinter import Tk, Canvas, CENTER
from PIL import Image, ImageTk

from dice_block import Block
from player import Player
from floor import Floor
from enemies import Ghost
from menu import Menu


# setups leaderboard file to save username, score and difficulty

logging.basicConfig(filename='leaderboard.txt',
                    filemode='a+',
                    format='',
                    level=logging.INFO)

KEYS = ['Left', 'Right', 'Up', 'Down', 'a', 'd', 'w', 's']
WINDOW_SIZE = (1280, 720)


class Game(Canvas):
    """
    A class that represents the Game Canvas.

    ---
    Attributes
    ---
    username : str
        username entered of the player
    width : int
        width of canvas
    height: int
        height of canvas
    difficulty : str
        game difficulty set at the start
    blocks : list
        list of Block objects
    score : int
        score of the current player

    Methods
    -------
    set_difficulty(difficulty='easy')
        Sets difficulty of game
    pause()
        Pauses Game
    unpause()
        Unpauses game
    save_game()
        Saves game state in file
    load_game(file)
        Loads specified file in parameter into game
    game_over()
        Logs score and username into leaderboard
    setup_game(game_state)
        Sets up game state in terms of player, enemies, leaderboard
    """

    def __init__(self, grid_size, username='Anonymous'):

        self.username = username
        self.width, self.height = grid_size
        self.difficulty = 'easy'

        super().__init__(width=self.width,
                         height=self.height,
                         background='#5f5f5f'
                         )

        # self.blocks saves the Block objects created
        self.blocks = []
        self._load_assets()

        self.score = 0

        # self._last_key is the last key pressed
        # when using the boss_key function
        self._last_key = ''
        self._mouse_held_down = False

        self._min_spawn_time = 1000
        self._max_spawn_time = 3000
        self._attack_timer_range = (4000, 6000)
        self._enemy_speed_x = -2
        # self.in_game is the state when the game is running
        self.in_game = False
        self.paused = False
        self._in_boss_page = False

        # tkinter after function variables
        self._player_after = None
        self._enemy_after = None
        self._create_enemy_after = None

        self._load_boss_images()

    def _load_boss_images(self):
        """Load images used for when the boss key is pressed."""
        vscode_icon = Image.open('./boss_key/vscode_ico.jpg')
        self.vscode_icon = ImageTk.PhotoImage(vscode_icon)

        tkinter_icon = Image.open('./boss_key/tkinter_ico.jpg')
        self.tk_icon = ImageTk.PhotoImage(tkinter_icon)

        excel_icon = Image.open('./boss_key/excel_ico.jpg')
        self.excel_icon = ImageTk.PhotoImage(excel_icon)

        excel1 = Image.open('./boss_key/Excel1.jpg')
        excel1 = excel1.resize((self.width, self.height))
        self.excel1 = ImageTk.PhotoImage(excel1)

        excel2 = Image.open('./boss_key/Excel2.jpg')
        excel2 = excel2.resize((self.width, self.height))
        self.excel2 = ImageTk.PhotoImage(excel2)

        python = Image.open('./boss_key/jupyter.jpg')
        python = python.resize((self.width, self.height))
        self.python = ImageTk.PhotoImage(python)

    def _initial_blocks(self, num_of_blocks):
        """Add initial Block objects to a list."""
        block_width = self.width/num_of_blocks

        # Creates (num_of_blocks - 4) amount of Block objects
        # where the sides and centers of the Game are blank

        for pos in range(1, num_of_blocks - 1):

            if pos not in [3, 4]:

                self.blocks.append(Block(
                                    (pos, 0),
                                    block_width,
                                    tag=f'Block{pos}'
                                    ))

    def _load_assets(self):
        """Create Object instances of game assets (player, floor etc.)."""
        self.floor = Floor()

        self._initial_blocks(8)
        self.player = Player((550,  687))

        # Defines a list with the objects
        # that make up the floor/ground of the game
        self.ground_list = [self.floor] + self.blocks

        self.enemy_list = []

    def _draw_assets(self):
        """Call the .draw() function from each object to show in Canvas."""
        for block in self.blocks:
            block.draw(self,
                       (2 + block.width * block.grid_pos[0]),
                       720 - (block.height * (block.grid_pos[1] + 1)))

        self.floor.draw(self)
        self.player.draw(self, self.player.pos_x, self.player.pos_y)

        # Sets the coordinate anchor of the player image to the center
        self.itemconfig(self.player.player, anchor=CENTER)

        # Creates a score text that updates with update_score function
        self.create_text(1150, 45,
                         text=f'Score: {self.score}',
                         font=('Segoe UI Variable Text Semibold', 24),
                         tag='score_tag')

        self.update_health()

    def update_health(self):
        """Update heart images in the canvas according to player health."""
        # Deletes existing health images
        self.delete('health')

        for health_index in range(self.player.health):
            self.create_image(
                              50 * (health_index + 1),
                              50,
                              image=self.player.img_hp,
                              tag='health'
                              )

    def update_score(self):
        """Update score text according to current score."""
        self.itemconfig(self.find_withtag('score_tag'),
                        text=f'Score: {self.score}'
                        )

    def _update_player(self):
        """Update player movement."""
        self.player.update(self)
        self.coords(self.player.player, self.player.pos_x, self.player.pos_y)

        if self.player.is_dead:
            self.game_over()
            return

        self._player_after = self.after(10, self._update_player)

    def _update_enemies(self):
        """Update all enemy movement and checks if they're dead."""
        remove_enemies = []

        for enemy in self.enemy_list:

            if not enemy.is_dead:
                enemy.update(self)
                self.coords(enemy.enemy, enemy.pos_x, enemy.pos_y)
            else:
                remove_enemies.append(enemy)

        # The enemy list is updated to only include enemies that are alive
        self.enemy_list = [enemy for enemy in self.enemy_list
                           if enemy not in remove_enemies]

        self._enemy_after = self.after(10, self._update_enemies)

    def _create_enemy(self):
        """Create enemy Objects (Ghost) and adds it to enemy list."""
        new_ghost = Ghost(self.player,
                          pos_x=random.choice([-100, 1380]),
                          pos_y=random.randint(50, int(self.height/2)),
                          shooting_delay=self._attack_timer_range,
                          speed_x=self._enemy_speed_x)

        new_ghost.draw(self)

        self.enemy_list.append(new_ghost)

        # Each enemy is generated after
        # a random spawn time based on the difficulty
        self._create_enemy_after = self.after(
                                        random.randint(self._min_spawn_time,
                                                       self._max_spawn_time),
                                        self._create_enemy
                                             )

    def set_difficulty(self, difficulty='easy'):
        """
        Set difficulty of the game.

        ---
        Parameters
        ---
        difficulty : str
            the difficulty of the game.
        """
        if difficulty == 'easy':

            self.player.health = 5
            self._min_spawn_time = 1000
            self._max_spawn_time = 2500
            self._attack_timer_range = (4000, 6000)
            self._enemy_speed_x = -2

        elif difficulty == 'med':

            self.player.health = 3
            self._min_spawn_time = 1000
            self._max_spawn_time = 2000
            self._attack_timer_range = (3000, 5000)
            self._enemy_speed_x = -3

        elif difficulty == 'hard':

            self.player.health = 1
            self._min_spawn_time = 1000
            self._max_spawn_time = 1500
            self._attack_timer_range = (2000, 4000)
            self._enemy_speed_x = -4

        self.difficulty = difficulty

    def clear_after_funcs(self):
        """Stop the after functions from executing."""
        self.after_cancel(self._player_after)
        self.after_cancel(self._create_enemy_after)
        self.after_cancel(self._enemy_after)

    def pause(self):
        """Pause game by stopping all updates."""
        self.clear_after_funcs()
        self.paused = True

    def unpause(self):
        """Unpause game by calling all update functions."""
        self._update_player()
        self._update_enemies()
        self._create_enemy()

        self.paused = False

    def save_game(self):
        """Save game state (username, player, score etc.) into a text file."""
        # save_index is the number of the file for the same username
        save_index = 0

        file_name = f'saved_game_{self.username}_{save_index}.txt'

        current_files = os.listdir('./saves')

        # checks whether the current file_name
        # is in the saves folder, else increment save_index

        while file_name in current_files:
            save_index += 1
            file_name = f'saved_game_{self.username}_{save_index}.txt'

        with open(file=f'./saves/{file_name}', mode='x', encoding='utf-8') as save_game_file:

            # Writes date and time, player,
            # enemy, score and difficulty info into file

            save_game_file.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')
            save_game_file.write(f'Player {self.player.health} {self.player.pos_x} {self.player.pos_y}\n')

            for enemy in self.enemy_list:
                save_game_file.write(f'Enemy {enemy._health} {enemy.pos_x} {enemy.pos_y} {enemy.direction}\n')

            save_game_file.write(f'Score {self.score}\n')
            save_game_file.write(f'Difficulty {self.difficulty}')

    def load_game(self, file):
        """Parse the save game file and sets up game with saved state."""
        self.username = file.split('_')[2]

        # each line in the save file corresponds
        # to a certain player/enemy or attribute
        with open(f'./saves/{file}', 'r', encoding='utf-8') as saved_game_file:
            attr = saved_game_file.read().split('\n')

        self.setup_game(game_state=attr)

    def game_over(self):
        """
        Set the game state to game over.

        logs score, username and difficulty into leaderboard.
        """
        self.in_game = False

        self.delete('all')
        self.clear_after_funcs()

        logging.info('%s,%s,%s', self.username, self.score, self.difficulty)

        # Game Over and Score text
        self.create_text(
            self.width/2,
            self.height/2,
            text='Game Over',
            font=('serif', 36)
            )

        self.create_text(
            self.width/2,
            self.height/2 + 50,
            text=f'Score: {self.score}',
            font=('serif', 24)
            )

        menu.create_game_over_buttons()

    def setup_game(self, game_state):
        """
        Set up game state.

        ---
        Parameters
        ---
        game_state : list
            if list empty, then game sets up as normal
            if list not empty, then game sets up according to list
            (saved game state)
        """
        self.score = 0
        self.in_game = True

        if self.paused:
            self.paused = False

        self._load_assets()

        # load game block

        if game_state:

            # gets all the attributes passed into game_state
            temp_list_player = game_state[1].split('Player ')
            player_attr = temp_list_player[1].split(' ')

            enemies = game_state[2: -2]
            score = game_state[-2].split(' ')[1]
            difficulty = game_state[-1].split(' ')[1]

            player_health = player_attr[0]
            player_pos = (float(player_attr[1]), float(player_attr[2]))

            # sets player attributes
            self.player.health = int(player_health)
            self.player.pos_x, self.player.pos_y = player_pos

            # sets enemy attributes
            for enemy in enemies:

                temp_list_enemy = enemy.split('Enemy ')
                enemy_attr = temp_list_enemy[1].split(' ')

                enemy_health = int(enemy_attr[0])
                enemy_pos = (float(enemy_attr[1]), float(enemy_attr[2]))
                enemy_dir = int(enemy_attr[3])

                new_enemy = Ghost(self.player)

                new_enemy.health = enemy_health
                new_enemy.pos_x, new_enemy.pos_y = enemy_pos

                new_enemy.direction = enemy_dir

                new_enemy.draw(self)

                self.enemy_list.append(new_enemy)

            # sets score and difficulty
            self.score = int(score)

        # calls all functions to set up game
        self.set_difficulty(self.difficulty)
        self._draw_assets()
        self._update_player()
        self._create_enemy()
        self._update_enemies()

        # key bindings
        root.bind('<KeyPress>', self.key_press)
        root.bind('<KeyRelease>', self.key_release)
        root.bind('<ButtonRelease-1>', self.mouse_button_release)
        root.bind('<B1-Motion>', self.mouse_button1_held)

    def _boss_key(self, key):
        """
        Handle function when boss key is pressed, shows different images.

        ---
        Parameters
        ---
        key : str
            key pressed passed from the key handler function
        """
        # If not in boss screen, it overlays an image over the pause menu
        if not self._in_boss_page:
            menu.show_pause_menu()
            self.pause()
            self._in_boss_page = True

        if self._in_boss_page:
            if self._last_key == key:
                root.title('Game')
                root.wm_iconphoto(False, self.tk_icon)
                self.delete('boss_img')

                self._in_boss_page = False
                self._last_key = ''
                if not self.in_game:
                    menu.back_to_menu()
                elif self.paused:
                    self.unpause()
                    menu.unpause()

        # either changes screen to image or switches from image to image
            else:

                menu.clear_buttons()

                if key == '1':
                    self._last_key = '1'
                    self.create_image(
                                    0,
                                    0,
                                    image=self.excel1,
                                    anchor='nw',
                                    tag='boss_img'
                                    )
                    root.title('Fishing Rod SKU.xlsx')
                    root.wm_iconphoto(False, self.excel_icon)

                if key == '2':
                    self._last_key = '2'
                    self.create_image(
                                    0,
                                    0,
                                    image=self.excel2,
                                    anchor='nw',
                                    tag='boss_img'
                                    )
                    root.title('For Website SKU.xlsx')
                    root.wm_iconphoto(False, self.excel_icon)

                if key == '3':
                    self._last_key = '3'
                    self.create_image(
                                    0,
                                    0,
                                    image=self.python,
                                    anchor='nw',
                                    tag='boss_img'
                                    )
                    root.title('Rod.ipynb')
                    root.wm_iconphoto(False, self.vscode_icon)

    def key_press(self, event):
        """
        Handle key press events.

        ---
        Parameters
        ---
        event : str
            passed from key binding
            key pressed
        """
        key = event.keysym

        # gets a modifier when certain keys are pressed (ctrl, alt etc.)
        modifier = event.state
        
        # boss_key handler  
        if key in ['1', '2', '3']:

            self._boss_key(key)

        # cheat code (invincibility) handler
        if modifier == 4 and key == 'space':
            self.player.invincibility()
            if self.player.invincible:
                self.create_text(
                                 1200,
                                 700,
                                 text='Invincibility On',
                                 tag='invincible'
                                 )
            else:
                self.delete('invincible')

        # cheat code (full-auto) handler
        if modifier == 4 and key == 'a':
            self.player.rapid_fire()
            if self.player.full_auto:
                self.create_text(
                                 1200,
                                 650,
                                 text='Full Auto On',
                                 tag='full_auto'
                                 )
            else:
                self.delete('full_auto')

        # handles in game key presses
        if self.in_game:

            if not self.paused:

                # player move left handler
                if key in ['Left', 'a']:

                    if self.player.image == self.player.img_right:
                        self.itemconfig(
                            self.player.player,
                            image=self.player.img_left,
                            anchor=CENTER
                            )
                        self.player.image = self.player.img_left
                        self.coords(self.player.player, 65, 0)

                    self.player.control(-self.player.speed, 0)

                # player move right handler
                if key in ['Right', 'd']:

                    if self.player.image == self.player.img_left:
                        self.itemconfig(
                            self.player.player,
                            image=self.player.img_right,
                            anchor=CENTER
                            )
                        self.player.image = self.player.img_right
                        self.coords(self.player.player, -65, 0)

                    self.player.control(self.player.speed, 0)

                # player jumps
                if key in ['Up', 'w', 'space']:
                    self.player.jump(self)

            # pause game handler
            if not self._in_boss_page:
                if key == 'Escape':

                    if self.paused:
                        self.unpause()
                        menu.unpause()
                    else:
                        self.pause()
                        menu.show_pause_menu()

    def key_release(self, event):
        """Handle key releases."""
        key = event.keysym

        # stops player movement handler
        if self.in_game:
            if key in ['Left', 'a']:
                self.player.control(0, 0)
            if key in ['Right', 'd']:
                self.player.control(0, 0)

    def mouse_button1_held(self, event):
        """Handle moving mouse whilst mouse button 1 is held."""
        # full-auto firing handler
        if self.player.full_auto:
            if self.in_game:
                if not self.paused:
                    mouse_position = (event.x, event.y)
                    self.player.shoot(self, mouse_position)

    def mouse_button_release(self, event):
        """Handle after mouse click."""
        # player shooting handler
        self._mouse_held_down = False

        if not self.player.full_auto:
            if self.in_game:
                if not self.paused:
                    mouse_position = (event.x, event.y)
                    self.player.shoot(self, mouse_position)


if __name__ == "__main__":

    # window, Game and Menu Instantiation
    root = Tk()
    root.title('Ghoster')
    root.resizable(False, False)

    new_game = Game(WINDOW_SIZE)
    new_game.pack()

    menu = Menu(root, new_game)
    menu.create_starting_buttons()

    root.mainloop()
