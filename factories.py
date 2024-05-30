from random import randrange as rand
from config import colors, shapes

class Factory:
    def create(self):
        pass

class ColorFactory(Factory):
    @staticmethod
    def create(index):
        return colors[index]


class ShapeFactory(Factory):
    @staticmethod
    def create():
        return shapes[rand(len(shapes))]


class StateFactory(Factory):
    @staticmethod
    def create(state_type, app):
        if state_type == 'PlayingState':
            from states import PlayingState
            return PlayingState(app)
        elif state_type == 'GameOverState':
            from states import GameOverState
            return GameOverState(app)
        else:
            raise ValueError(f"Unknown state type: {state_type}")