class Floor():
    """
    Floor class.

    ---
    Methods
    ---
    draw(canvas)
        Creates a floor object (rectangle) in the game
        for collision purposes
    """

    def __init__(self):
        pass

    def draw(self, canvas):
        """
        Create a floor object (rectangle) in the game for collision purposes.

        ---
        Parameters
        ---
        canvas : Game Canvas
            Reference to Game Canvas Object in main.py
        """
        canvas.create_rectangle(
                                -100,
                                canvas.height,
                                canvas.width + 100,
                                canvas.height,
                                tag='floor'
                               )
