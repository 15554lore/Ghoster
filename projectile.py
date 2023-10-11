import math


class Projectile():
    """
    Projectile Class that handles projectile movement and collision.

    ---
    Attributes
    ---
    pos_x : int
        x position of projectile
    pos_y : int
        y position of projectile
    coords : 2-tuple or 4-tuple
        current coordinates of projectile
    image : Tkinter PhotoImage
        image of projectile (currently only fireball)
    projectile : int
        reference to projectile in canvas
    projectile_after : str
        reference to projectile after function in canvas
    ---
    Methods
    ---
    shoot(starting_x, starting_y, canvas, target_pos)
        Creates image of projectile and determines shooting vector
    shooting_after(self, canvas, projectile, projectile_dir)
        Handles movement and collision check of projectile
    """

    def __init__(self, tag, pos_x, pos_y, target, image=None):

        self._tag = tag

        self.pos_x, self.pos_y = pos_x, pos_y
        self.coords = None

        # offset is the size or length of projectile

        self._offset = 15

        self.image = image
        self._target = target

        self._shooting_angle = 0

        # unit vector (delta_x, delta_y)
        self._delta_x, self._delta_y = 0, 0

        self.projectile = None
        self.projectile_after = None

    def _get_shooting_angle(self, target_pos):
        """
        Calculate the angle to shoot along. Uses trigonometric properties.

        ---
        Returns
        ---
        theta : float
            shooting angle
        """
        triangle_y = abs(self.pos_y - target_pos[1])
        triangle_x = abs(self.pos_x - target_pos[0])

        # Checks if the target position is directly below projectile
        # and sets angle accordingly

        if triangle_x == float(0):
            theta = math.pi/2
        else:
            theta = math.atan(triangle_y/triangle_x)

        return theta

    def _calculate_bullet_pos(self, theta, target_pos):
        """Calculate the unit vector * projectile size (_offset)."""
        # calculates side length of triangle

        delta_x = self._offset * math.cos(theta)
        delta_y = self._offset * math.sin(theta)

        # Reflects delta_x or delta_y if target
        # is above or to the left of bullet
        if target_pos[0] < self.pos_x:
            delta_x = -delta_x
        if target_pos[1] > self.pos_y:
            delta_y = -delta_y

        return delta_x, delta_y

    def _check_collision(self, canvas):
        """Return True if collision with target. Else returns False."""
        # self.coords is empty (target dead or deleted)

        if not self.coords:
            return True

        # self.coords is only 2-tuple, fireball image

        if len(self.coords) == 2:

            collision_list = canvas.find_overlapping(
                self.coords[0] - 25,
                self.coords[1] - 25,
                self.coords[0] + 25,
                self.coords[1] + 25
                )
        # self.coords is 4-tuple, bullet line

        else:
            collision_list = canvas.find_overlapping(
                self.coords[0],
                self.coords[1],
                self.coords[2],
                self.coords[3]
                )

        # get all refernce tags of target, floor and block

        target_tags = canvas.find_withtag(self._target)
        floor_tags = canvas.find_withtag('floor')
        block_tags = canvas.find_withtag('Block')

        combined_tags = target_tags + floor_tags + block_tags

        # only get ID of collided objects
        # if in combined tags (wanted collisions)

        specific_collision = [ID for ID in collision_list
                              if ID in combined_tags]

        if specific_collision:
            return True
        return False

    def _update_coords(self, canvas):
        """Update current coordinates of projectile."""
        self.coords = canvas.coords(self.projectile)

    def shoot(self, starting_x, starting_y, canvas, target_pos):
        """
        Create the image/line of the projectile and handles initial direction.

        ---
        Parameters
        ---
        starting_x : int
            initial x position of projectile
        starting_y : int
            initial y position of projectile
        canvas : Game Object
            reference to Game Canvas Object in main.py
        target_pos : 2-tuple or 4-tuple
            coordinates of the target object/reference
        """
        self._shooting_angle = self._get_shooting_angle(target_pos)
        self._delta_x, self._delta_y = self._calculate_bullet_pos(
                                                        self._shooting_angle,
                                                        target_pos
                                                                )

        # fireball image

        if self.image is not None:
            self.projectile = canvas.create_image(
                starting_x,
                starting_y + 25,
                image=self.image,
                tags=self._tag
                )

        # bullet line

        else:
            self.projectile = canvas.create_line(
                starting_x,
                starting_y - 1,
                starting_x + self._delta_x,
                starting_y - self._delta_y,
                width=5,
                fill='yellow',
                tags=self._tag
                )

        self._update_coords(canvas)

        self.shooting_after(
                            canvas,
                            self.projectile,
                            (self._delta_x, self._delta_y)
                           )

    def shooting_after(self, canvas, projectile, projectile_dir):
        """
        Handle movement and collision of projectile.

        ---
        Parameters
        ---
        canvas : Game Object
            reference to Game Canvas Object in main.py
        projectile : int
            reference to projectile object in Canvas
        projectile_dir : 2-tuple
            direction of the projectile in a tuple
        """
        if self._check_collision(canvas):

            canvas.delete(self.projectile)
            return

        # manipulates pos_x and pos_y to fit for boundary check
        if len(self.coords) == 2:
            pos_x, pos_y = self.coords
            pos_x0, pos_x1 = (pos_x, pos_x)
            pos_y0, pos_y1 = (pos_y, pos_y)

        elif len(self.coords) == 4:
            pos_x0, pos_x1 = (self.coords[0], self.coords[2])
            pos_y0, pos_y1 = (self.coords[1], self.coords[3])

        # boundary check
        if pos_x1 >= 1280 or pos_x0 <= 0 or pos_y0 <= 0 or pos_y1 >= 720:
            canvas.delete(projectile)

        else:

            if not canvas.paused:
                canvas.move(projectile, projectile_dir[0], -projectile_dir[1])
                self._update_coords(canvas)

            self.projectile_after = canvas.after(
                25,
                self.shooting_after,
                canvas,
                projectile,
                projectile_dir
                )
