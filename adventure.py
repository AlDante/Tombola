"""
Move with a Sprite Animation

Simple program to show basic sprite usage.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_move_animation
"""
import argparse
import math
import random
import sys
from typing import List, Tuple

import arcade
import pandas as pd
from pandas import DataFrame
from pyglet import media

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Weihnachtstombola 2020 - es kann nur eine(n) geben. Plus neun andere."

IRON_KNIGHT = "./resources/sounds/Dark Fantasy Studio- Superheroes/mp3/" \
              "Dark Fantasy Studio- Iron knight (seamless).mp3"
RADAR = "./resources/sounds/Tarannos/Radar-MasterEffects.wav"
DEMOLITION_RACE = "./resources/sounds/Dark Fantasy Studio- PIXEL Faster stronger harder/" \
                  "mp3/5- Dark Fantasy Studio - Demolition race.mp3"
DONT_BELIEVE_IN_LOVE = "./resources/sounds/Tarannos/She-Dont-Believe-In-Love.mp3"

INSTRUCTION_SOUND = IRON_KNIGHT
GAME_SOUND = DEMOLITION_RACE
WINNERS_SOUND = RADAR
GAME_OVER_SOUND = DONT_BELIEVE_IN_LOVE

COIN_SCALE = 0.5
# DEBUG_COIN_COUNT must be more than 10, otherwise game screen is never shown
DEBUG_COIN_COUNT = 15
CHARACTER_SCALING = 1

COIN_DIAMETER = 10

# How fast to move, and how fast to run the animation
MOVEMENT_SPEED = 8
UPDATES_PER_FRAME = 5
MABEL_SPEED = MOVEMENT_SPEED

# Volume of the background music
VOLUME = 0.01

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Padding for the coins
PADDING = 25

def is_debug():
    """
    Returns true if running in debugger
    Can be overwritten to be always true to speed testing
    """

    # return True
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


class MyConfig:
    """
    Configuration used by practically all views.
    :param lose: data frame of player names and number of lives
    :param winners: list of winners, filled at end of game
    :return: none
    """

    volume: float  # Volume of the sound, between 0 and 1

    def __init__(self, lose: DataFrame, prizes: List[str], winners: list = None):
        self.lose = lose
        self.prizes = prizes

        # Actually want an empty list as a default, but that leads to mutable errors
        if winners is None:
            self.winners = []
        else:
            self.winners = winners


class MyView(arcade.View):
    """
    Standard members for the views.
    :param config: configuration for the view (e.g. list of player names)
    :param next_view: view to move on to when this one is done, None if end of game.
    :return: none
    """

    def __init__(self, config: MyConfig, next_view=None):
        super().__init__()
        self.config = config
        self.next_view = next_view


class MyCoin(arcade.Sprite):
    """
    Standard members for the coins.
    :param filename: filename for sprite data
    :param scale: scaling for sprite.
    :param name: player name to attach to the coin
    :param lives: number of lives the player has (equals number of tickets bought).
    :return: none
    """

    def __init__(self, filename: str = None, scale: float = 1, name: str = None, lives: int = 0):
        # Set up parent class
        super().__init__(filename, scale)
        self.name = name
        self.lives = lives


class PlayerCharacter(arcade.Sprite):
    """
    Characteristics for Mabel. Mabel is the figure who collects the coins.
    """

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = CHARACTER_SCALING

        # Generate a random angle between -180 and 180 degrees (-pi and pi radians)
        theta = random.randint(-180, 180)
        self.change_x = MABEL_SPEED * math.sin(math.radians(theta))
        self.change_y = MABEL_SPEED * math.cos(math.radians(theta))

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

    def update(self, delta_time: float = 1 / 60):

        # Generate a random angle between -90 and 90 degrees (-pi/2 and pi/2 radians)
        theta = random.randint(-90, 90)
        x_changed = False

        # Change direction if end of screen
        if self.left < COIN_DIAMETER:
            # Hit left edge of screen. X velocity must be set positive, y velocity +ve or -ve.
            # Angle between -90 and 90 (quadrant 1 and 4, ⊃)
            # add nothing to the angle
            self.change_x = MABEL_SPEED * math.cos(math.radians(theta))
            self.change_y = MABEL_SPEED * math.sin(math.radians(theta))
            x_changed = True
        elif self.right > SCREEN_WIDTH - COIN_DIAMETER:
            # Hit right edge of screen. X velocity must be set negative, y velocity +ve or -ve.
            # Angle between 90 and -90 (quadrant 2 and 3, ⊂)
            # Add 180 degrees to the angle
            self.change_x = MABEL_SPEED * math.cos(math.radians(theta + 180))
            self.change_y = MABEL_SPEED * math.sin(math.radians(theta + 180))
            x_changed = True

        if self.top > SCREEN_HEIGHT - COIN_DIAMETER:
            # Hit right edge of screen. Y velocity must be set negative, X velocity +ve or -ve.
            # Angle between 180 and 0 (quadrant 3 and 4 ⋃)
            # Subtract 90 degrees from the angle
            if x_changed:
                # If x already changed, only update y
                self.change_y = -1 * abs(self.change_y)
            else:
                # Otherwise update both x and y
                self.change_x = MABEL_SPEED * math.cos(math.radians(theta - 90))
                self.change_y = MABEL_SPEED * math.sin(math.radians(theta - 90))

        elif self.bottom < COIN_DIAMETER:
            # Hit bottom edge of screen. Y velocity must be set positive, X velocity +ve or -ve.
            # Angle between 0 and 180 (quadrant 1 and 2, ⋂ )
            # Add 90 degrees to the angle
            if x_changed:
                # If x already changed, only update y
                self.change_y = abs(self.change_y)
            else:
                # Otherwise update both x and y
                self.change_x = MABEL_SPEED * math.cos(math.radians(theta + 90))
                self.change_y = MABEL_SPEED * math.sin(math.radians(theta + 90))

        super(PlayerCharacter, self).update()


class WinnersView(MyView):
    """ View to show winners """

    def __init__(self, config: MyConfig, next_view: MyView = None):
        """ Set up the game and initialize the variables. """
        super().__init__(config, next_view)

        """ Load music and set flag that currently no music playing"""
        self.sound_song = arcade.load_sound(WINNERS_SOUND)
        self.music_playing: media.Player = None

    def on_show(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        arcade.draw_text("Winners Screen", SCREEN_WIDTH / 2, 14 * SCREEN_HEIGHT / 16,
                         arcade.color.WHITE, font_size=50, anchor_x="center")

        """ List all the winners """
        i = 12
        for (winner, prize) in self.config.winners:
            arcade.draw_text(f'{winner} - {prize}', SCREEN_WIDTH / 8, i * SCREEN_HEIGHT / 16,
                             arcade.color.WHITE, font_size=20, anchor_x="left")
            i -= 1

        arcade.draw_text("Click to advance", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 8,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

        """ When drawing for the first time, play sound"""
        if not self.music_playing:
            self.music_playing = self.sound_song.play(self.config.volume, loop=True)

    def on_mouse_press(self, _x, _y, _button, _modifiers):

        """If the user presses the mouse button, show closing credits. """
        self.sound_song.stop(self.music_playing)
        self.next_view.setup()
        self.window.show_view(self.next_view)


class GameOverView(MyView):
    """ View to show closing credits when game is over """

    def __init__(self, config: MyConfig, next_view: MyView = None):
        """ This is run once when we switch to this view """
        super().__init__(config, next_view)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)
        """ Load music and set flag that currently no music playing"""
        self.sound_song = arcade.load_sound(GAME_OVER_SOUND)
        self.music_playing: media.Player = None

        self.text_color = arcade.color.WHITE

        # Font sizes for title, song credits, artist attribution and production credits
        self.title_font_size = 50.0
        self.production_font_size = 30.0
        self.credit_font_size = 20.0
        self.attribution_font_size = 15.0
        self.leading = 6  # gap between lines
        self.credits_list = None

    def setup(self):
        self.credits_list = arcade.SpriteList()
        
        self.credits_list.append(self.credit_contribution("\n" * 5, 14 * SCREEN_HEIGHT / 25))
        
        # self.centre_text_on_screen("Credits", 14 * SCREEN_HEIGHT / 16, text_color, title_font_size)

        self.credits_list.append(self.credit_contribution("IRON KNIGHT and PIXEL", 13 * SCREEN_HEIGHT / 25))
        self.credits_list.append(self.credit_attribution("written and performed by Nicolas "
                                                         "Jeudy, Dark Fantasy Studio.",
                                                         13 * SCREEN_HEIGHT / 25 - self.leading
                                                         - self.attribution_font_size))

        self.credits_list.append(self.credit_contribution("RADAR", 11 * SCREEN_HEIGHT / 25))
        self.credits_list.append(self.credit_attribution("written and performed by Tarannos, "
                                                         "Welsh Thunder Records.",
                                                         11 * SCREEN_HEIGHT / 25 - self.leading
                                                         - self.attribution_font_size))

        self.credits_list.append(self.credit_contribution("DON'T BELIEVE IN LOVE ", 9 * SCREEN_HEIGHT / 25))
        self.credits_list.append(self.credit_attribution("Written by Tarannos and performed by "
                                                         "Tarannos, Ray and Sonja Jenkins.",
                                                         9 * SCREEN_HEIGHT / 25 - self.leading
                                                         - self.attribution_font_size))
        self.credits_list.append(self.credit_attribution("A Ray Jenkins Production for Welsh "
                                                         "Thunder Records.",
                                                         9 * SCREEN_HEIGHT / 25 -
                                                         2 * self.leading -
                                                         2 * self.attribution_font_size))

        self.credits_list.append(
            self.credit_contribution("Concept, animation and design by David Jenkins",
                                     6 * SCREEN_HEIGHT / 25))

        self.credits_list.append(self.credit_contribution("Debugging by Jana Leible",
                                                          5 * SCREEN_HEIGHT / 25))

        self.credits_list.append(self.credit_contribution("Sprites by Kenney", 4 * SCREEN_HEIGHT / 25))

        self.credits_list.append(self.credit_production("A PYTHON ARCADE PRODUCTION", 2 * SCREEN_HEIGHT / 25))

        # Let the text move upwards
        for sprite in self.credits_list:
            sprite.change_x = 0
            sprite.change_y = 0.5

    def on_show(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        # arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, 14 * SCREEN_HEIGHT / 16)

    @staticmethod
    def centre_text_on_screen(text: str, start_y: float, color: arcade.Color, font_size: float,
                              width: int = 900) -> arcade.Sprite:
        """
        :param text: – Text to draw
        :param start_y: – y coordinate of the lower-left point to start drawing text
        :param color:  – Color of the text
        :param font_size: – Size of the text
        :param width: – Width of the text-box for the text to go into. Used with alignment.
        """
        sprite = arcade.draw_text(text, SCREEN_WIDTH / 2, start_y, color, font_size, width, align="center",
                                  anchor_x="center", anchor_y="baseline")
        return sprite

    def title(self, text: str) -> arcade.Sprite:
        sprite = self.centre_text_on_screen(text, 14 * SCREEN_HEIGHT / 16, self.text_color, self.title_font_size,
                                            width=900)
        return sprite

    def credit_contribution(self, text: str, start_y: float, width: int = 900) -> arcade.Sprite:
        sprite = self.centre_text_on_screen(text, start_y, self.text_color, self.credit_font_size, width)
        return sprite

    def credit_attribution(self, text: str, start_y: float, width: int = 900) -> arcade.Sprite:
        sprite = self.centre_text_on_screen(text, start_y, self.text_color,
                                            self.attribution_font_size, width)
        return sprite

    def credit_production(self, text: str, start_y: float, width: int = 900) -> arcade.Sprite:
        sprite = self.centre_text_on_screen(text, start_y, self.text_color, self.production_font_size, width)
        return sprite

    def on_draw(self):

        # self.window.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

        """ Draw this view """
        # This command has to happen before we start drawing
        arcade.start_render()
        self.title("Credits")

        self.credit_contribution("Click anywhere to end", SCREEN_HEIGHT / 16)

        # self.window.set_viewport(0, SCREEN_WIDTH - 1, SCREEN_HEIGHT / 16, 14 * SCREEN_HEIGHT / 16)

        # Let the text move upwards
        for sprite in self.credits_list:
            if sprite.top > 14 * SCREEN_HEIGHT / 16:
                sprite.remove_from_sprite_lists()

        # Draw all the sprites.
        self.credits_list.draw()

        """ When drawing for the first time, play sound"""
        if not self.music_playing:
            self.music_playing = self.sound_song.play(self.config.volume, loop=True)

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player
        self.credits_list.update()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """If the user presses the mouse button, end the game. """
        self.sound_song.stop(self.music_playing)
        self.window.close()


class InstructionView(MyView):
    """ View to show instructions """

    def __init__(self, config: MyConfig, next_view: MyView = None):
        """ Set up the game and initialize the variables. """
        # super().__init__(width, height, title)
        super().__init__(config, next_view)

        """ Load music and set flag that currently no music playing"""
        self.sound_song = arcade.load_sound(INSTRUCTION_SOUND)
        self.music_playing: media.Player = None

    @staticmethod
    def setup():
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

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
        arcade.draw_text("Ihr fangt irgendwo zufällig verteilt auf der Wiese an.", SCREEN_WIDTH / 8,
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
        if self.music_playing is None:
            self.music_playing = self.sound_song.play(volume=self.config.volume)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """If the user presses the mouse button, play the game. """

        self.sound_song.stop(self.music_playing)
        # next_view = GameView(self.lose)
        self.next_view.setup()
        self.window.show_view(self.next_view)


def map_prizes_to_winners(winners: List[str], prizes: List[str]) -> List[Tuple[str, str]]:

    random.shuffle(winners)
    random.shuffle(prizes)

    return list(zip(winners, prizes))


def random_coin_position() -> Tuple[int, int]:
    return (
        random.randrange(COIN_DIAMETER + PADDING, SCREEN_WIDTH - COIN_DIAMETER - PADDING),
        random.randrange(COIN_DIAMETER + PADDING, SCREEN_HEIGHT - COIN_DIAMETER - PADDING)
    )


class GameView(MyView):
    """ Main application class. """

    def __init__(self, config: MyConfig, next_view: MyView):
        """ Set up the game and initialize the variables. """
        super().__init__(config, next_view)

        # No mouse cursor
        self.window.set_mouse_visible(False)
        # self.screen_width = screen_width
        # self.screen_height = screen_height

        # Sprite lists
        self.player_list = None
        self.coin_list = None

        """ Load music and set flag that currently no music playing"""
        self.sound_song = arcade.load_sound(GAME_SOUND)
        self.music_playing: media.Player = None

        self.lose = config.lose

        self.max_coins = len(config.lose.index)

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
        # self.player.velocity = (5,0)
        self.player.change_x = MOVEMENT_SPEED
        self.player.change_y = 0

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player.scale = 0.8

        self.player_list.append(self.player)

        for i in range(self.max_coins):
            l_name = self.lose.iloc[i]["Name"]
            l_lose = self.lose.iloc[i]["Lose"]
            coin = MyCoin(":resources:images/items/gold_1.png",
                          scale=0.5, name=l_name, lives=l_lose)
            # coin.center_x = COIN_DIAMETER + random.randrange(PADDING, (SCREEN_WIDTH - 2 * COIN_DIAMETER) - PADDING)
            # coin.center_y = COIN_DIAMETER + random.randrange(PADDING, (SCREEN_HEIGHT - 2 * COIN_DIAMETER) - PADDING)
            coin.center_x, coin.center_y = random_coin_position()

            self.coin_list.append(coin)

        self.score = len(self.coin_list)

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
        output = f"{self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, font_size=60)

        """ When drawing for the first time, play sound"""
        if self.music_playing is None:
            self.music_playing = self.sound_song.play(self.config.volume, loop=True)

    def on_update(self, delta_time):
        """ Movement and game logic """

        """Stop when there are as many coins as prizes left (i.e. 10 winners)"""
        if len(self.coin_list) <= len(self.config.prizes):
            winners = [obj.name for obj in self.coin_list]
            winners_with_prizes = map_prizes_to_winners(winners, self.config.prizes)

            # Save winners to file
            with open('winners.txt', "w") as f:
                for (name, prize) in winners_with_prizes:
                    f.write(f"{name} - {prize}\n")

            self.sound_song.stop(self.music_playing)
            self.config.winners = winners_with_prizes
            # next_view = WinnersView(winners)
            self.window.set_mouse_visible(True)
            self.window.show_view(self.next_view)

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
                coin.center_x, coin.center_y = random_coin_position()

                # Change colour when lives get low, but not initially to not show up people with only one ticket.
                if coin.lives == 3:
                    coin.color = arcade.color.BRASS
                elif coin.lives == 2:
                    coin.color = arcade.color.ORANGE_PEEL
                elif coin.lives == 1:
                    coin.color = arcade.color.CANDY_APPLE_RED
            else:
                coin.remove_from_sprite_lists()

        self.score = len(self.coin_list)


def read_prizes(prizes_file: str) -> List[str]:

    with open(prizes_file, 'r') as file:
        prizes = file.readlines()

    return prizes


def main():
    """ Main method """

    parser = argparse.ArgumentParser(description='Weihnachtstombola.')
    parser.add_argument('-i', metavar='excelfile', dest='excelfile', type=str, required=True,
                        help='Pfad zur Excel Datei, die die Namen und Lose enthält.')
    parser.add_argument('-p', metavar='prizes', dest='prizes', type=str, required=True,
                        help='Pfad zu einer .txt-Datei, die die Preise enthält.')

    args = parser.parse_args()
    print(args.excelfile)

    import os
    print(os.getcwd())

    df_lose = pd.read_excel(args.excelfile)
    prizes = read_prizes(args.prizes)
    config = MyConfig(df_lose, prizes)
    config.volume = VOLUME

    # window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window = arcade.Window(fullscreen=True, title=SCREEN_TITLE)

    global SCREEN_HEIGHT, SCREEN_WIDTH

    left, SCREEN_WIDTH, bottom, SCREEN_HEIGHT = window.get_viewport()
    # SCREEN_WIDTH = screen_width
    # SCREEN_HEIGHT = screen_height

    # Set up window sequence
    # Start with Instruction View -> GameView -> WinnersView -> GameOverView
    game_over_view = GameOverView(config)
    game_over_view.setup()
    winners_view = WinnersView(config, game_over_view)
    game_view = GameView(config, winners_view)
    start_view = InstructionView(config, game_view)
    start_view.setup()
    window.show_view(start_view)
    arcade.run()

    print("Finished")


if __name__ == "__main__":
    main()
