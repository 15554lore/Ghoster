class Block():
    """
    Block class for block object in the game.

    ---
    Attributes
    ---
    grid_pos : 2-tuple
        position in canvas if there was a grid
    width : int
        width of block
    height : int
        height of block
    tag : str
        reference tag of block
    block_num : int
        reference number of block
    ---
    Methods
    ---
    draw(canvas, pos_x, pos_y)
        Creates rectangle of block in Canvas
    """

    def __init__(self, grid_pos, width, tag):

        self.grid_pos = grid_pos
        self.width = width
        self.height = 125
        self.tag = tag
        self.block_num = int(tag[-1])

    def draw(self, canvas, pos_x, pos_y):
        """
        Create rectangle of block in canvas.

        ---
        Parameters
        ---
        canvas : Game Object
            Reference to Game Canvas Object in main.py
        pos_x : int
            initial x position of block
        pos_y : int
            initial y position of block
        """
        canvas.create_rectangle(pos_x, pos_y,
                                pos_x + self.width, pos_y + self.height,
                                tag="Block",
                                width=2,
                                fill='grey')
