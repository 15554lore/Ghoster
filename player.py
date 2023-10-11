from PIL import Image, ImageTk
from projectile import Projectile


class Player():
    """
    Player class that handles player movement and attributes.

    ---
    Attributes
    ---
    pos_x : int
        x position of player
    pos_y : int
        y position of player
    width : int
        width of player image
    height : int
        height of player image
    player : int
        reference to player object in Canvas
    health : int
        current health of player
    is_dead : bool
        boolean for if player is dead
    speed : int
        speed of player
    invincible : bool
        boolean for cheat code (invincible)
    full_auto : bool
        boolean for cheat code (full_auto)
    ---
    Methods
    ---
    draw(canvas, pos_x, pos_y)
        Creates image of player sprite in canvas at (pos_x, pos_y)
    invincibility()
        Negates boolean of player invincibility
    rapid_fire()
        Negates boolean of player full auto
    gravity()
        Sets player y-axis movement downwards
    control(move_x, move_y=0)
        Sets player x,y axis movement according to move_x, move_y respectively
    jump()
        Sets player is_jumping boolean to True and is_falling to False
    update(canvas)
        Handles player movement
    shoot(canvas, mouse_pos)
        Handles player shooting
    """

    def __init__(self, pos):

        self._load_images()

        self.pos_x, self.pos_y = pos
        self.width, self.height = 66, 76
        self._half_width = int(self.width / 2)
        self._half_height = int(self.height / 2)
        self._check_floor_y = self.pos_y - self._half_height

        self.player = None
        self.health = 1
        self.is_dead = False

        self.speed = 7

        self.fireballs_hit = []

        self._is_jumping = False
        self._is_falling = False

        self._move_x = 0
        self._move_y = 0

        self.invincible = False
        self.full_auto = False

    def _load_images(self):
        """
        Load all images for the player.

        ---
        Attributions
        ---
        Health sprite:  file='./images/heart_full_16x16.png'
                        author=C.Nilsson
                        link="https://opengameart.org/content/simple-small-pixel-hearts"
                        date=20/11/2022
                        Under CC-BY-SA 3.0 License
        """
        player_sprite_right = Image.open('./images/sprite2.png')
        player_sprite_right = player_sprite_right.resize((66, 76))
        player_sprite_right = ImageTk.PhotoImage(player_sprite_right)

        player_sprite_left = Image.open('./images/sprite2Flipped.png')
        player_sprite_left = player_sprite_left.resize((66, 76))
        player_sprite_left = ImageTk.PhotoImage(player_sprite_left)

        health_image = Image.open('./images/heart_full_16x16.png')
        health_image = health_image.resize((30, 30))
        health_image = ImageTk.PhotoImage(health_image)

        self.img_hp = health_image

        self.img_left = player_sprite_left
        self.img_right = player_sprite_right

        # sets initial image to right facing sprite
        self.image = player_sprite_right

    def _update_check_floor_y(self):
        """Update the y pos of the bottom of the image."""
        self._check_floor_y = self.pos_y + self._half_height

    def draw(self, canvas, pos_x, pos_y):
        """
        Create image of player sprite at (pos_x, pos_y).

        ---
        Parameters
        ---
        canvas : Game Object
            Reference to Game Canvas object in main.py
        pos_x : int
            x position of player image
        pos_y : int
            y position of player image
        """
        self.player = canvas.create_image(
            pos_x,
            pos_y - self._half_height,
            image=self.image,
            tag='player',
            anchor='center')

    def invincibility(self):
        """Negate boolean of player invincibility."""
        self.invincible = not self.invincible

    def rapid_fire(self):
        """Negate boolean of player full_auto shooting."""
        self.full_auto = not self.full_auto

    def gravity(self):
        """Set y-axis movement of player downwards."""
        self._move_y += 2.0

    def control(self, move_x, move_y=0):
        """Set x, y axis movement of player to move_x, move_y respectively."""
        self._move_x = move_x
        self._move_y = move_y

    def jump(self, canvas):
        """
        Set player is_jumping boolean to True and is_falling to False.

        Only if player is not jumping
        """
        if self._grounded(canvas):
            self._is_falling = False
            self._is_jumping = True

    def _grounded(self, canvas):
        """Return if player is touching floor or block top."""
        # gets list of block references from canvas
        block_list = canvas.find_withtag('Block')
        block_coordinates = []
        for block_ref in block_list:
            block_coordinates.append(canvas.coords(block_ref))

        # selects the x-coordinates of the block
        # and the top y-coordinate of the block for the range
        block_ranges = [(coor[0], coor[2], coor[1])
                        for coor in block_coordinates]

        floor_coordinates = []

        # Adds in extra ranges to account for the floor
        for index, ranges in enumerate(block_ranges):
            # if block doesn't touch left wall
            if index == 0:
                if ranges[0] > 0:
                    floor_coordinates.append((0, ranges[0], 720))
            # if block doesn't touch right wall
            elif index == len(block_ranges) - 1:
                if ranges[1] < 1280:
                    floor_coordinates.append((ranges[1], 1280, 720))
            # spaces inbetween blocks
            else:
                next_range = block_ranges[index + 1]
                if ranges[1] != next_range[0]:
                    floor_coordinates.append((ranges[1], next_range[0], 720))

        floor_coordinates += block_ranges

        # checks if x position of player is within range
        # and if the y position of player is on/below the floor
        # it will adjust the y position of the player
        for floor_range in floor_coordinates:
            if floor_range[0] <= self.pos_x <= floor_range[1]:
                if self._check_floor_y >= floor_range[2]:
                    self.pos_y = floor_range[2] - self._half_height
                    return True
        return False

    def _check_hp_is_zero(self):
        """Return player is dead when health is 0."""
        if self.health == 0:
            self.is_dead = True
        return self.is_dead

    def _get_hit_list(self, canvas):
        """Return a list of objects colliding with the player."""
        pos = canvas.coords(self.player)

        # sets bounding box of player to pos

        pos = [
            pos[0] - self._half_width,
            pos[1] - self._half_height,
            pos[0] + self._half_width,
            pos[1] + self._half_height
            ]

        self_hit_list = canvas.find_overlapping(pos[0], pos[1], pos[2], pos[3])

        return self_hit_list

    def _moving_into_block(self, block_coord):
        """
        Return if player is moving into a block.

        ---
        Parameters
        ---
        block_coord : 4-tuple
            Tuple containing bounding box of Block object
        """
        # sets future position of player
        temp_x, temp_y = (self.pos_x + self._move_x, self.pos_y + self._move_y)

        pos_x_0, pos_y_0, pos_x_1, pos_y_1 = block_coord

        # checks whether future position of player
        # will be within the bounding box

        if (pos_x_0 <= temp_x <= pos_x_1 and pos_y_0 <= temp_y <= pos_y_1):
            return True

    def update(self, canvas):
        """
        Handle player movement.

        ---
        Parameters
        ---
        canvas : Game Object
            Reference to Game Canvas Object in main.py
        """
        if self._check_hp_is_zero():
            canvas.delete(self.player)
            return

        self.gravity()

        if self._is_falling and self._grounded(canvas):
            self._move_y = 0

        if self._grounded(canvas) and not self._is_jumping:
            self._move_y = 0

        if self._is_jumping and not self._is_falling:
            self._is_falling = True
            self._move_y -= 30

        # Handles collision with blocks

        collision_list = self._get_hit_list(canvas)
        block_list = [ID for ID in collision_list
                      if ID in canvas.find_withtag('Block')]
        fireball_list = [ID for ID in collision_list
                         if ID in canvas.find_withtag('fireball')]

        # Handles hit by enemy fireball

        if not self.invincible:
            for fireball in fireball_list:

                if fireball not in self.fireballs_hit:
                    self.fireballs_hit.append(fireball)

                    self.health -= 1
                    canvas.update_health()

        for block in block_list:

            block_pos = canvas.coords(block)
            block_x0, block_y0, blockx1, blocky1 = block_pos

            if self._moving_into_block(block_pos) and self.pos_y > block_y0:

                self._move_x = 0

        if self.pos_x + self._move_x >= 1280:
            self._move_x = 0
        if self.pos_x + self._move_x <= 0:
            self._move_x = 0

        self.pos_x += self._move_x
        self.pos_y += self._move_y
        self._update_check_floor_y()

    def shoot(self, canvas, mouse_pos):
        """
        Handle player shooting action.

        ---
        Parameters
        ---
        canvas : Game Object
            reference to Game Canvas Object in main.py
        mouse_pos : 2-tuple
            current mouse position
        """
        if self.is_dead:
            return

        # Creates new Projectile (bullet for player)
        new_bullet = Projectile(
                                tag='bullet',
                                pos_x=self.pos_x,
                                pos_y=self.pos_y,
                                target='enemy'
                                )
        new_bullet.shoot(self.pos_x, self.pos_y - 1, canvas, mouse_pos)
