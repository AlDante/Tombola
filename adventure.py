"""
Move with a Sprite Animation

Simple program to show basic sprite usage.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_move_animation
"""
import argparse
import random
import sys

import arcade
import pandas as pd

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Move with a Sprite Animation Example"

COIN_SCALE = 0.5
DEBUG_COIN_COUNT = 10
CHARACTER_SCALING = 1

COIN_DIAMETER = 10

# How fast to move, and how fast to run the animation
MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 5

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


def is_debug():

    if getattr(sys, 'gettrace', None) is None:
        print('No sys.gettrace')
        return False
    else:
        return sys.gettrace()


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    :param filename: absolute path to textures
    :return: none
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class MyCoin(arcade.Sprite):
    def __init__(self, filename: str = None, scale: float = 1, name: str = None, lives: int = 0):
        # Set up parent class
        super().__init__(filename, scale)
        self.name = name
        self.lives = lives


class PlayerCharacter(arcade.Sprite):
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = CHARACTER_SCALING

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = ":resources:images/animated_characters/female_adventurer/femaleAdventurer"
        # main_path = ":resources:images/animated_characters/female_person/femalePerson"
        # main_path = ":resources:images/animated_characters/male_person/malePerson"
        # main_path = ":resources:images/animated_characters/male_adventurer/maleAdventurer"
        # main_path = ":resources:images/animated_characters/zombie/zombie"
        # main_path = ":resources:images/animated_characters/robot/robot"

        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]


class GameOverView(arcade.View):
    """ View to show when game is over """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()
        self.texture = arcade.load_texture("resources/images/game_over.png")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)
        """ Load music and set flag that currently no music playing"""
        self.sound_song = arcade.load_sound("./resources/sounds/Tarannos/Radar-MasterEffects.wav")
        self.music_playing = False

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

        """ When drawing for the first time, play sound"""
        if not self.music_playing:
            arcade.play_sound(self.sound_song)
            self.music_playing = True

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, exit the game. """
        arcade.stop_sound(self.sound_song)
        self.window.close()
        """"exit(0)"""


class InstructionView(arcade.View):
    """ View to show instructions """

    def __init__(self, df_lose):
        """ Set up the game and initialize the variables. """
        # super().__init__(width, height, title)
        super().__init__()
        self.df_lose = df_lose

        """ Load music and set flag that currently no music playing"""
        self.sound_song = arcade.load_sound(
            "./resources/sounds/Dark Fantasy Studio- Superheroes/mp3/Dark Fantasy Studio- Iron knight (seamless).mp3")
        self.music_playing = False

    def on_show(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        arcade.draw_text("Instructions Screen", SCREEN_WIDTH / 2, 14 * SCREEN_HEIGHT / 16,
                         arcade.color.WHITE, font_size=50, anchor_x="center")

        arcade.draw_text("Mabel sammelt die Lose ein. Ihr habt alle so viele Leben, wie ihr Lose gekauft habt.",
                         SCREEN_WIDTH / 8, 12 * SCREEN_HEIGHT / 16,
                         arcade.color.WHITE, font_size=20, anchor_x="left")
        arcade.draw_text("Ihr fängt irgendwo zufällig verteilt auf der Wiese an.", SCREEN_WIDTH / 8,
                         11 * SCREEN_HEIGHT / 16,
                         arcade.color.WHITE, font_size=20, anchor_x="left")
        arcade.draw_text("Wenn ihr noch Leben habt, erscheint euer Losmünze wieder irgendwo zufällig.",
                         SCREEN_WIDTH / 8, 10 * SCREEN_HEIGHT / 16,
                         arcade.color.WHITE, font_size=20, anchor_x="left")
        arcade.draw_text("Wenn ihr nur noch wenige Leben habt, werden die Lose orange und dann rot.", SCREEN_WIDTH / 8,
                         9 * SCREEN_HEIGHT / 16,
                         arcade.color.WHITE, font_size=20, anchor_x="left")
        arcade.draw_text("Die letzten zehn Namen gewinnen.", SCREEN_WIDTH / 8, 8 * SCREEN_HEIGHT / 16,
                         arcade.color.WHITE, font_size=20, anchor_x="left")

        arcade.draw_text("Click to advance", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 8,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

        """ When drawing for the first time, play sound"""
        if not self.music_playing:
            arcade.play_sound(self.sound_song)
            self.music_playing = True

    def on_mouse_press(self, _x, _y, _button, _modifiers):

        """If the user presses the mouse button, start the game. """
        arcade.stop_sound(self.sound_song)
        next_view = GameView(self.df_lose)
        next_view.setup()
        self.window.show_view(next_view)


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self, df_lose):
        """ Set up the game and initialize the variables. """
        # super().__init__(width, height, title)
        super().__init__()

        # No mouse cursor
        self.window.set_mouse_visible(False)

        # Sprite lists
        self.player_list = None
        self.coin_list = None

        """ Load music and set flag that currently no music playing"""
        self.sound_song = arcade.load_sound(
            "./resources/sounds/Dark Fantasy Studio- PIXEL Faster stronger harder/mp3/5- Dark Fantasy Studio - Demolition race.mp3")
        self.music_playing = False

        self.df_lose = df_lose

        self.max_coins = len(df_lose.index)

        if is_debug():
            print("Anzahl Lose: ", self.max_coins, "wurde für Debug runtergesetzt. Jetzt: ", DEBUG_COIN_COUNT)
            self.max_coins = DEBUG_COIN_COUNT

        # Set up the player
        self.score = 0
        self.player = None

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player = PlayerCharacter()

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player.scale = 0.8

        self.player_list.append(self.player)

        for i in range(self.max_coins):
            l_name = self.df_lose.iloc[i]["Name"]
            l_lose = self.df_lose.iloc[i]["Lose"]
            coin = MyCoin(":resources:images/items/gold_1.png",
                          scale=0.5, name=l_name, lives=l_lose)
            coin.center_x = COIN_DIAMETER + random.randrange(SCREEN_WIDTH - 2 * COIN_DIAMETER)
            coin.center_y = COIN_DIAMETER + random.randrange(SCREEN_HEIGHT - 2 * COIN_DIAMETER)

            self.coin_list.append(coin)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.coin_list.draw()
        self.player_list.draw()

        for coin in self.coin_list:
            arcade.draw_text(coin.name, coin.center_x, coin.center_y, arcade.color.WHITE, 12)

        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

        """ When drawing for the first time, play sound"""
        if not self.music_playing:
            arcade.play_sound(self.sound_song)
            self.music_playing = True

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """
        if key == arcade.key.UP:
            self.player.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user releases a key.
        """
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player
        self.player_list.update()

        # Update the players animation
        self.player_list.update_animation()

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in hit_list:
            coin.lives = coin.lives - 1
            if coin.lives > 0:
                coin.center_x = COIN_DIAMETER + random.randrange(SCREEN_WIDTH - 2 * COIN_DIAMETER)
                coin.center_y = COIN_DIAMETER + random.randrange(SCREEN_HEIGHT - 2 * COIN_DIAMETER)

                # Change colour when lives get low, but not initially to not show up people with only one ticket.
                if coin.lives == 3:
                    coin.color = arcade.color.BRASS
                elif coin.lives == 2:
                    coin.color = arcade.color.ORANGE_PEEL
                elif coin.lives == 1:
                    coin.color = arcade.color.CANDY_APPLE_RED
            else:
                coin.remove_from_sprite_lists()

            self.score += 1

        """Stop when there are 10 coins left (i.e. 10 winners)"""
        if len(self.coin_list) <= 10:
            arcade.stop_sound(self.sound_song)
            game_over_view = GameOverView()
            self.window.set_mouse_visible(True)
            self.window.show_view(game_over_view)


def main():
    """ Main method """

    parser = argparse.ArgumentParser(description='Weihnachtstombola.')
    parser.add_argument('-i', metavar='excelfile', dest='excelfile', type=str,
                        help='Pfad zur Excel Datei, die die Namen und Lose enthält.')

    args = parser.parse_args()
    print(args.excelfile)

    import os
    print(os.getcwd())

    df_lose = pd.read_excel(args.excelfile)

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView(df_lose)
    window.show_view(start_view)
    # start_view.setup()
    arcade.run()

    print("Finished")


if __name__ == "__main__":
    main()
