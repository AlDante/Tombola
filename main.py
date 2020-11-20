"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)
        self.text_angle = 0
        self.time_elapsed = 0.0

        # If you have sprite lists, you should create them here,
        # and set them to None

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here
        pass

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        # start_x and start_y make the start point for the text. We draw a dot to make it easy to see
        # the text in relation to its start x and y.
        start_x = 50
        start_y = 450
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        Sprite = arcade.draw_text("Simple line of text in 12 point", start_x, start_y, arcade.color.BLACK, 12)

        """
        start_x = 50
        start_y = 150
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("Garamond Text", start_x, start_y, arcade.color.BLACK, 15, font_name='GARA')

        start_x = 50
        start_y = 400
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("Text anchored 'top' and 'left'.",
                         start_x, start_y, arcade.color.BLACK, 12, anchor_x="left", anchor_y="top")

        start_y = 350
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("14 point multi\nline\ntext",
                         start_x, start_y, arcade.color.BLACK, 14, anchor_y="top")

        start_y = 450
        start_x = 300
        width = 200
        height = 20
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_lrtb_rectangle_outline(start_x, start_x + width,
                                           start_y + height, start_y,
                                           arcade.color.BLUE, 1)
        arcade.draw_text("Centered Text.",
                         start_x, start_y, arcade.color.BLACK, 14, width=200, align="center")

        start_y = 250
        start_x = 300
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("Text centered on\na point",
                         start_x, start_y, arcade.color.BLACK, 14, width=200, align="center",
                         anchor_x="center", anchor_y="center")

        start_y = 150
        start_x = 300
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("Text rotated on\na point", start_x, start_y,
                         arcade.color.BLACK, 14, width=200, align="center", anchor_x="center",
                         anchor_y="center", rotation=self.text_angle)

        start_y = 150
        start_x = 20
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("Sideways text", start_x, start_y,
                         arcade.color.BLACK, 14, width=200, align="center",
                         anchor_x="center", anchor_y="center", rotation=90.0)

        start_y = 20
        start_x = 50
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text(f"Time elapsed: {self.time_elapsed:7.1f}",
                         start_x, start_y, arcade.color.BLACK, 14)
        """
        

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.text_angle += 1
        self.time_elapsed += delta_time

        pass

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        pass

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
