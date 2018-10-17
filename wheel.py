from collections import namedtuple

import pygame

import random
import itertools
import datetime

Resolution = namedtuple('Resolution', 'x y')

from test_messages import messages as MESSAGES

# IMPORTANT CONSTANTS
RESOLUTION = Resolution(800, 600)  # Don't go too low or you'll get Fatal error
SHORT_END = min(RESOLUTION)
WHEEL_TEXT = 'FORTUNE'
FONT = 'Comic Sans MS'
SOUND_FILE = None  # .wav file to play after wheel spins

# COLORS
BG_COLOR = pygame.Color('blue')
COLOR_LEFT = pygame.Color('red')
COLOR_RIGHT = pygame.Color('green')
COLOR_WHEEL_TEXT = pygame.Color('purple')
MESSAGE_COLOR = pygame.Color('yellow')


class Wheel:
    def __init__(self, speed=5, spin_length=3):
        pygame.init()
        pygame.font.init()

        self.sound = pygame.mixer.Sound(SOUND_FILE) if SOUND_FILE else None
        self.font = pygame.font.SysFont(FONT, SHORT_END // 20)
        self.big_font = pygame.font.SysFont(FONT, SHORT_END // 10)
        self.message = ""
        self.text_area = None  # Records area that was written to by text blit

        self.speed = speed
        self.spin_length = datetime.timedelta(seconds=spin_length)
        self.spin_start = None  # Datetime

        self.screen = pygame.display.set_mode(RESOLUTION)
        self.wheel = self.get_wheel(
            wheel_text=WHEEL_TEXT,
            color_left=COLOR_LEFT,
            color_right=COLOR_RIGHT,
            color_text=COLOR_WHEEL_TEXT,
            radius=(SHORT_END // 2 - SHORT_END // 10),
        )
        self.state = self.stage_normal  # Really hacky state machine

    def get_wheel(self, wheel_text, color_left, color_right, color_text, radius):
        size = (radius * 2, radius * 2)
        pos = (radius, radius)

        left_half = pygame.Surface(size, pygame.SRCALPHA)
        right_half = pygame.Surface(size, pygame.SRCALPHA)

        pygame.draw.circle(left_half, color_left, pos, radius)
        pygame.draw.circle(right_half, color_right, pos, radius)

        right_half = right_half.subsurface(pygame.Rect(radius, 0, radius, radius * 2))  # Gets right half of circle
        left_half.blit(right_half, (radius, 0))

        text = self.big_font.render(wheel_text, False, color_text)

        left_half.blit(
            text,
            (  # Center of wheel
                (left_half.get_width() - text.get_width()) // 2,
                (left_half.get_width() - text.get_height()) // 2,
            )
        )

        return left_half

    def display_wheel(self, wheel_surface):
        self.screen.blit(
            wheel_surface,
            (  # Center of screen
                (self.screen.get_width() - wheel_surface.get_width()) // 2,
                (self.screen.get_height() - wheel_surface.get_height()) // 2 - 15,
            )
        )

    def run(self):
        self.screen.fill(BG_COLOR)
        self.display_wheel(self.wheel)  # Display initial wheel

        for i in itertools.count():
            if pygame.event.peek(pygame.QUIT):
                exit(1)
            else:
                self.state(i)
            pygame.display.update()

    def stage_normal(self, i):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.spin_start = datetime.datetime.now()
                self.state = self.stage_spinning

    def stage_spinning(self, i):
        def stop_spinning():
            self.message = get_message(MESSAGES)
            if self.sound:
                self.sound.play()
            self.state = self.stage_result

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                stop_spinning()

        # TODO: Move this to on_enter
        self.screen.fill(BG_COLOR, rect=self.text_area)
        self.display_wheel(self.wheel)

        rot_wheel = pygame.transform.rotate(self.wheel, i * self.speed)
        self.display_wheel(rot_wheel)

        if datetime.datetime.now() - self.spin_start > self.spin_length:
            stop_spinning()

    def stage_result(self, i):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.state = self.stage_normal

        text = self.font.render(self.message, False, MESSAGE_COLOR)
        self.text_area = self.screen.blit(
            text,
            (
                (self.screen.get_width() - text.get_width()) // 2,
                self.screen.get_height() - text.get_height(),
            )
        )


# TODO: There might be a better way to do this
def get_message(messages):
    total_prob = sum(message.probability for message in messages)

    rand = random.uniform(0, total_prob)
    probability_so_far = 0
    for message in messages:
        if probability_so_far + message.probability < rand:
            probability_so_far += message.probability
        else:
            return message.string


if __name__ == '__main__':
    wheel = Wheel()
    wheel.run()
