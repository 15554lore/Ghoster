import random

from tkinter import CENTER
from PIL import Image, ImageTk

from projectile import Projectile


class Ghost():
    """
    Ghost class (enemy) that handles movement and shooting.

    ---
    Attributes
    ---
    enemy : int
        reference to ghost object in Canvas
    pos_x : int
        x position of ghost
    pos_y : int
        y position of ghost
    speed_x : int
        x-axis movement speed of ghost
    speed_y : int
        y-axis movement speed of ghost
    direction : int
        direction that ghost moves in (-1, left) (1, right)
    width : int
        width of ghost image
    height : int
        height of ghost image
    player_ref : int
        reference to player in Canvas
    is_dead : bool
        boolean for if the ghost is dead
    ---
    Methods
    ---
    draw(canvas)
        creates image of ghost in Canvas
    update(canvas)
        handles movement and collision checking of ghost
    shoot(canvas)
        handles fireball shooting of ghost
    """

    def __init__(self,
                 player_ref,
                 pos_x=-50,
                 pos_y=50,
                 shooting_delay=(4000, 7000),
                 speed_x=-2):

        self._health = 3
        self.enemy = None

        self.pos_x, self.pos_y = pos_x, pos_y

        # checks if ghost is spawned on the right or left of canvas
        # and sets direction of ghost
        self.speed_x, self.speed_y = speed_x, 0
        if self.pos_x > 1280:
            self.direction = -1
        else:
            self.direction = 1

        self._move_x, self._move_y = 0, 0
        self._load_image()

        self.width, self.height = (76, 66)

        self._bullets_hit = []

        # first time the ghost has moved
        self._first_movement_stretch = True

        min_delay, max_delay = shooting_delay
        self._shooting_delay = random.randint(min_delay, max_delay)

        # timer for pausing whilst shooting
        self._movement_timer = 0

        # timer for moving downwards
        self._moving_down_timer = 0

        self.player_ref = player_ref
        self._is_shooting = False
        self.is_dead = False

    def _load_image(self):
        """
        Load images needed for the ghost.

        ---
        Attributions
        ---
        ghost.png is under CC0 license
        """
        image = Image.open('./images/ghost.png')
        image = image.resize((76, 66))
        self.image = ImageTk.PhotoImage(image)

        fireball_image = Image.open('./images/ghost.png')
        fireball_image = image.resize((50, 50))
        self.fireball_image = ImageTk.PhotoImage(fireball_image)

    def draw(self, canvas):
        """
        Create image of ghost in Canvas.

        ---
        Parameters
        ---
        canvas : Game Object
            References the Game Canvas Object in main.py
        """
        self.enemy = canvas.create_image(
            self.pos_x,
            self.pos_y,
            image=self.image,
            anchor=CENTER,
            tag='enemy'
            )

    def _at_wall(self):
        """Check whether the ghost is by the boundary."""
        # Sets first time crossing the wall from spawn
        right_side_x = self.pos_x + self.width/2
        left_side_x = self.pos_x - self.width/2

        if left_side_x > 0 and right_side_x < 1280:
            self._first_movement_stretch = False

        # Returns if left or right side is touching wall
        if not self._first_movement_stretch:

            return right_side_x >= 1280 or left_side_x <= 0

        return False

    def _below_screen(self):
        """Check whether ghost is below the canvas."""
        return self.pos_y - self.height/2 > 720

    def _set_shooting_status(self, canvas):
        """Handle ghost shooting mechanism."""
        if not self.player_ref.is_dead and not self.is_dead:
            self.shoot(canvas)
            self._is_shooting = False

    def _check_collision(self, canvas):
        """Handle collision checks and returns a list of colliding objects."""
        pos = canvas.coords(self.enemy)

        # Gets bounding box of ghost
        pos = [
            pos[0] - int(self.width/2),
            pos[1] - int(self.height/2),
            pos[0] + int(self.width/2),
            pos[1] + int(self.height/2)
            ]

        self_hit_list = canvas.find_overlapping(pos[0], pos[1], pos[2], pos[3])

        return self_hit_list

    def update(self, canvas):
        """
        Handle movement and calls for collision checks of ghost.

        ---
        Parameters
        ---
        canvas : Game Object
            references the Game Canvas Object in main.py
        """
        if self._below_screen():

            canvas.delete(self.enemy)
            self.is_dead = True
            return

        # Checks for collision with bullet shot from player
        collision_list = self._check_collision(canvas)
        bullet_list = [ID for ID in collision_list
                       if ID in canvas.find_withtag('bullet')]

        # Handles bullet collision
        for bullet in bullet_list:
            if bullet not in self._bullets_hit:
                self._bullets_hit.append(bullet)
                self._health -= 1

        # Handles dying of ghost
        if self._health <= 0:
            canvas.delete(self.enemy)
            self.is_dead = True
            canvas.score += 100
            canvas.update_score()
            return

        # Stops movement if ghost is shooting
        if self._is_shooting:
            self._move_x = 0

        # Handles movement of ghost
        else:

            if self._movement_timer >= self._shooting_delay:

                self._is_shooting = True
                self._delay_movement(canvas)
                self._movement_timer = 0

            else:

                # Ghost stops at canvas boundary and moves down
                if self._at_wall():

                    if self._moving_down_timer >= 500:
                        self.direction = -self.direction
                        self._move_y = 0
                        self._move_x = abs(self.speed_x) * self.direction
                        self._moving_down_timer = 0

                    else:
                        self._move_y = 1
                        self._move_x = 0
                        self._moving_down_timer += 10
                else:
                    self._move_x = abs(self.speed_x) * self.direction

                self._movement_timer += 10

                self.pos_x += self._move_x
                self.pos_y += self._move_y

    def _delay_movement(self, canvas):
        """Stop movement of ghost when shooting."""
        canvas.after(250, lambda c=canvas: self._set_shooting_status(c))

    def shoot(self, canvas):
        """
        Handle shooting action of ghost.

        ---
        Parameters
        ---
        canvas : Game Object
            References the Game Canvas Object in main.py
        """
        player_coords = canvas.coords(self.player_ref.player)

        new_fireball = Projectile(
            tag='fireball',
            pos_x=self.pos_x,
            pos_y=self.pos_y,
            target='player',
            image=self.fireball_image
            )

        new_fireball.shoot(self.pos_x, self.pos_y, canvas, player_coords)
