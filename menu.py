from tkinter import Button, Text
import os


class Menu():
    """
    Menu class that handles with the starting game menu and buttons.

    ---
    Attributes
    ---
    game : Game Object Reference
        References the Game Object in main.py
    root : Tkinter.Tk() object
        References the root window
    buttons_shown : list
        List of Button Objects on the current Canvas
    """

    def __init__(self, root, game):

        self.game = game
        self.buttons_shown = []
        self.root = root

        self._buttons_setup()

    def _buttons_setup(self):
        """Instantiate all the Buttons for the Menu."""
        self.start_game_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Start Game',
            command=self._start_game
            )
        self.leaderboard_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Leaderboard',
            command=self._show_leaderboard
            )
        self.settings_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Settings',
            command=self._show_settings
            )
        self.load_game_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Load Game',
            command=self._show_load_menu
            )
        self.username_box = Text(
            self.game,
            width=20,
            height=1,
            font=('Helvetica', 16)
            )
        self.continue_btn = Button(
            self.game,
            width=20,
            height=2,
            text='Restart',
            command=lambda: self._start_game(replay=True)
            )
        self.back_to_menu_btn = Button(
            self.game,
            text='Back to Main Menu',
            command=lambda: self.back_to_menu(ingame=True)
            )
        self.save_game_btn = Button(
            self.game,
            text='Save Game',
            command=self._save
            )
        self.save_and_quit_btn = Button(
            self.game,
            text='Save and Quit',
            command=lambda _quit=True: self._save(quit_game=_quit)
            )
        self.clear_saves_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Clear saves',
            command=self._clear_saves
            )
        self.back_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Return to Main Menu',
            command=self.back_to_menu
            )
        self.difficulty_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Game Difficulty',
            command=self._show_difficulty_settings
            )
        self.easy_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Easy',
            command=lambda difficulty='easy': self._set_difficulty(difficulty)
            )
        self.medium_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Medium',
            command=lambda difficulty='med': self._set_difficulty(difficulty)
            )
        self.hard_btn = Button(
            self.game,
            width=25,
            height=2,
            text='Hard',
            command=lambda difficulty='hard': self._set_difficulty(difficulty)
            )

    def create_starting_buttons(self):
        """Place Main menu page buttons and text."""
        self.start_game_btn.place(
                                  x=self.game.width/2 - 100,
                                  y=(self.game.height/3)
                                 )

        self.leaderboard_btn.place(
                                   x=self.game.width/2 - 100,
                                   y=(self.game.height/3) + 100
                                  )

        self.settings_btn.place(
                                x=self.game.width/2 - 100,
                                y=(self.game.height/3) + 200
                               )

        self.load_game_btn.place(
                                 x=self.game.width/2 - 100,
                                 y=(self.game.height/3) + 300
                                )

        # Name Label next to username box
        self.game.create_text(
            self.game.width/2 - 10,
            150,
            text='Ghoster',
            font=('Comic Sans', 50, 'bold'),
            fill='brown',
            tag='title'
        )
        self.game.create_text(
            self.game.width/2 - 150,
            695,
            text='Username: ',
            font=('Yu Gothic', 16), tag='name_label'
            )

        self.username_box.place(x=self.game.width/2 - 50, y=680)

        self.buttons_shown.append(self.start_game_btn)
        self.buttons_shown.append(self.leaderboard_btn)
        self.buttons_shown.append(self.settings_btn)
        self.buttons_shown.append(self.load_game_btn)
        self.buttons_shown.append(self.username_box)

    def create_game_over_buttons(self):
        """Game Over screen button placement."""
        self.buttons_shown.append(self.continue_btn)
        self.buttons_shown.append(self.back_to_menu_btn)

        self.back_to_menu_btn.config(width=20, height=2)
        self.continue_btn.place(
                                x=self.game.width/2 - 150,
                                y=self.game.height/2 + 100
                               )
        self.back_to_menu_btn.place(
                                    x=self.game.width/2 + 50,
                                    y=(self.game.height/2 + 100)
                                   )

    def show_pause_menu(self):
        """Pause menu button and background placement."""
        # Pause menu background
        self.game.create_rectangle(
            self.game.width/2 - 100,
            self.game.height/2 - 200,
            self.game.width/2 + 100,
            self.game.height/2 + 200,
            fill='#BEBEBE',
            outline='orange',
            width=5,
            tag='paused'
            )

        # Paused Text
        self.game.create_text(
            self.game.width/2,
            self.game.height/2 - 150,
            text='Paused',
            font=('helvitica', 24),
            tag='paused'
            )

        self.back_to_menu_btn.place(
                                    x=self.game.width/2 - 50,
                                    y=self.game.height/3 + 50
                                   )

        self.save_game_btn.place(
                                 x=self.game.width/2 - 30,
                                 y=self.game.height/3 + 100
                                )

        self.save_and_quit_btn.place(
                                     x=self.game.width/2 - 35,
                                     y=self.game.height/3 + 150
                                    )

        self.buttons_shown.append(self.back_to_menu_btn)
        self.buttons_shown.append(self.save_and_quit_btn)
        self.buttons_shown.append(self.save_game_btn)

    def unpause(self):
        """Clear pause menu."""
        self.game.delete('paused')
        self.clear_buttons()

    def _save(self, quit_game=False):
        """Call game save function, destroys root window if quit_game True."""
        self.game.save_game()

        if quit_game:
            self.root.destroy()

    def _clear_saves(self):
        """Clear all save files in saves directory."""
        save_files = os.listdir('./saves')
        for file in save_files:
            os.remove(f'./saves/{file}')

        # reloads the load menu
        self._show_load_menu()

    def _show_load_menu(self):
        """Load menu button placement and create buttons for each save file."""
        self.clear_buttons()

        self.clear_saves_btn.place(x=self.game.width/2 + 25, y=650)

        self.game.create_text(
                              self.game.width/2,
                              50,
                              text='Saved Games',
                              font=('helvetica', 24)
                             )
        current_save_files = os.listdir('./saves')

        # Creates a Button Object
        # for each save file with username and date on it

        for index, file_name in enumerate(current_save_files):
            username = file_name.split('_')[-2]
            with open(f'./saves/{file_name}', 'r', encoding='utf-8') as saved_game_file:
                attr = saved_game_file.read().split('\n')
            datetime = attr[0]
            load_file_btn = Button(
                self.game,
                width=30,
                height=2,
                text=f'{username}      {datetime}',
                command=lambda file=file_name: self.load_game(file=file)
                )
            load_file_btn.place(
                                x=self.game.width/2 - 105,
                                y=100 + (50 * (index + 1))
                            )
            self.buttons_shown.append(load_file_btn)

        self.back_btn.place(x=self.game.width/2 - 200, y=650)

        self.buttons_shown.append(self.back_btn)
        self.buttons_shown.append(self.clear_saves_btn)

    def load_game(self, file):
        """
        Clear screen and calls the load game function with the save file.

        ---
        Parameters
        ---
        file : str
            filename of save file
        """
        self.game.delete('all')
        self.clear_buttons()
        self.game.load_game(file=file)

    def _show_settings(self):
        """Place Settings menu button and text."""
        self.clear_buttons()

        self.game.create_text(
            self.game.width/2,
            50,
            text='Settings',
            font=('Yu Gothic', 36),
            tag='settings_label'
            )

        self.difficulty_btn.place(x=self.game.width/2 - 100, y=200)

        self.back_btn.place(x=self.game.width/2 - 100, y=650)

        self.buttons_shown.append(self.back_btn)
        self.buttons_shown.append(self.difficulty_btn)

    def _show_difficulty_settings(self):
        """Difficulty menu button placement."""
        self.clear_buttons()

        self.easy_btn.place(x=self.game.width/2 - 100, y=200)

        self.medium_btn.place(x=self.game.width/2 - 100, y=300)

        self.hard_btn.place(x=self.game.width/2 - 100, y=400)

        self.buttons_shown.append(self.easy_btn)
        self.buttons_shown.append(self.medium_btn)
        self.buttons_shown.append(self.hard_btn)

    def _set_difficulty(self, difficulty):
        """
        Call set difficulty function with desired difficulty selected.

        ---
        Parameters
        ---
        difficulty : str
            selected difficulty for game
        """
        self.game.set_difficulty(difficulty)

        self.clear_buttons()
        self._show_settings()

    def _sort_top10_scores(self, scores):
        """
        Sort the scores given leaderboard.txt lines.

        ---
        Parameters
        ---
        scores : list of list
            list of individual lines which are split
            into username, score and difficulty
        """
        scores_sorted = sorted(
            scores,
            key=lambda score_entry: int(score_entry[1]), reverse=True
            )

        return scores_sorted

    def _list_scores(self, score_list, offset):

        for index, score_entry in enumerate(score_list[:10]):

            username = score_entry[0]
            score = score_entry[1].strip('\n')

            self.game.create_text(
                self.game.width/2 - 150 + offset,
                50 * (index + 3),
                text=f'#{index + 1}',
                font=('helvetica', 20)
                )
            self.game.create_text(
                self.game.width/2 - 50 + offset,
                50 * (index + 3),
                text=f'{username}',
                font=('helvetica', 20)
                )
            self.game.create_text(
                self.game.width/2 + 150 + offset,
                50 * (index + 3),
                text=f'{score}',
                font=('helvetica', 20)
                )

    def _show_leaderboard(self):
        """Leaderboard menu button and high score text placement."""
        self.clear_buttons()

        with open('leaderboard.txt', 'r', encoding='utf-8') as leaderboard:
            scores = leaderboard.readlines()

        scores = list(map(lambda x: x.split(','), scores))

        easy_scores = [score for score in scores if score[2] == 'easy\n']
        medium_scores = [score for score in scores if score[2] == 'med\n']
        hard_scores = [score for score in scores if score[2] == 'hard\n']

        easy_scores_sorted = self._sort_top10_scores(easy_scores)
        medium_scores_sorted = self._sort_top10_scores(medium_scores)
        hard_scores_sorted = self._sort_top10_scores(hard_scores)
        scores_sorted = self._sort_top10_scores(scores)

        # High Score text

        self.game.create_text(
            self.game.width/2,
            50,
            text='High Scores',
            font=('helvetica', 24)
            )

        self.game.create_text(
            self.game.width/2 - 400,
            100,
            text='Easy',
            font='Arial 16 bold'
        )
        self.game.create_text(
            self.game.width/2,
            100,
            text='Medium',
            font='Arial 16 bold'
        )
        self.game.create_text(
            self.game.width/2 + 400,
            100,
            text='Hard',
            font='Arial 16 bold'
        )
        # Create text for each score
        self._list_scores(easy_scores_sorted, -400)
        self._list_scores(medium_scores_sorted, 0)
        self._list_scores(hard_scores_sorted, 400)
        self.back_btn.place(x=self.game.width/2 - 50, y=650)
        self.buttons_shown.append(self.back_btn)

    def back_to_menu(self, ingame=False):
        """Exit back to main menu from game or from other menu pages."""
        if ingame:
            self.game.clear_after_funcs()
            self.game.in_game = False
            self.game.paused = False

        self.game.delete('all')
        self.clear_buttons()

        self.create_starting_buttons()

    def clear_buttons(self):
        """Destroy all buttons on the screen and deletes all labels."""
        self.game.delete('name_label')
        self.game.delete('settings_label')
        self.game.delete('title')
        for btn in self.buttons_shown:
            btn.destroy()

        # Resets button_shown list for next use

        self.buttons_shown = []

        self._buttons_setup()

    def _start_game(self, replay=False):
        """
        Call the setup_game function.

        If new game, gets the current username entered
        """
        if not replay:

            username = self.username_box.get("1.0", "end-1c")
            if username.strip() == '':
                self.game.username = 'Anonymous'
            else:
                self.game.username = username

        self.game.delete('all')
        self.clear_buttons()

        # game_state is set as empty list, new game
        self.game.setup_game([])
