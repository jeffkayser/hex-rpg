#!/usr/bin/env python
# -=- coding: utf-8 -=-

"""
Python command-line implementation of Hex by Jeff Moore.
http://www.1km1kt.net/rpg/Hex
"""

from __future__ import division, print_function, unicode_literals

import random


def roll(n=1, d=6, keys=0):
    return sum([random.randint(1, d) + keys for _ in range(n)])


class GameOverError(Exception):
    pass

class Game(object):
    def init_rooms(self):
        self.room_actions = {
            0: {
                'w': {'action': self.weapon_up, 'prompt': "magic [w]eapon"},
                'a': {'action': self.armor_up, 'prompt': "magic [a]rmor"},
                'f': {'action': self.move, 'prompt': "[f]ind new dungeon"}
                },
            1: {
                'r': {'action': self.rest, 'prompt': "[r]est"},
                's': {'action': self.scavenge, 'prompt': "[s]cavenge"}
                },
            2: {
                't': {'action': self.trigger_trap, 'prompt': "[t]rigger trap"},
                'd': {'action': self.disable_trap, 'prompt': "[d]isable trap"}
                },
            3: {
                'r': {'action': self.rest, 'prompt': "[r]est"},
                's': {'action': self.scavenge, 'prompt': "[s]cavenge"}
                },
            4: {
                'r': {'action': self.run, 'prompt': "[r]un"},
                'f': {'action': self.fight, 'prompt': "[f]ight"}
                },
            5: {
                'r': {'action': self.run, 'prompt': "[r]un"},
                'f': {'action': self.fight, 'prompt': "[f]ight"}
                },
            6: {
                's': {'action': self.search, 'prompt': "[s]earch"}
                },
            7: {
                'd': {'action': self.descend, 'prompt': "[d]escend"}
                },
            8: {
                'f': {'action': self.fightboss, 'prompt': "[f]ight boss"}
                },
            9: {
                'e': {'action': self.exit, 'prompt': "[e]xit"}
                },
        }

    def new_run(self):
        self.moves = 0
        self.health = 6
        self.endurance = 6
        self.lvl = 1
        self.weapon = 0
        self.armor = 0
        self.location = 0

    def reset(self):
        self.new_run()
        self.xp = 0
        self.keys = 0

    def __init__(self):
        self.init_rooms()
        self.reset()

    def health_up(self, change):
        if change < 0:
            change += self.armor
        self.health += change

    def endurance_up(self, change):
        if change < 0:
            change += self.weapon
        self.endurance += change

    def weapon_up(self, change=1):
        if self.xp >= 50 * change:
            self.xp -= 50 * change
            self.weapon += change

    def armor_up(self, change=1):
        if self.xp >= 50 * change:
            self.xp -= 50 * change
            self.armor += change

    def action(self, what):
        what()
        if self.location != 0:
            self.end_room()
            if what != self.move:
                self.move()

    def end_room(self):
        if self.health <= 0 or self.endurance <= 0:
            print("You are defeated.")
            self.xp //= 2
            raise GameOverError()

    def room_desc(self, n=None):
        if n is None:
            n = self.location
        if n == 1:
            return "in an empty corridor"
        elif n == 2:
            return "in a trap room"
        elif n == 3:
            return "in an empty room"
        elif n == 4:
            return "in a monster room"
        elif n == 5:
            return "in a monster corridor"
        elif n == 6:
            return "in a treasure room"
        elif n == 7:
            return "at the stairs down"
        elif n == 8:
            return "in the boss monster room"
        elif n == 9:
            return "at the dungeon exit"
        else:
            return "in a town bazaar"

    def show_where(self):
        print("You find yourself {}.".format(self.room_desc(self.location)))

    def show_prompt(self):
        prompt = ', '.join([item['prompt'] for item in iter(
            self.room_actions[self.location].values())])
        print("Actions: {}".format(prompt))

    def show_stats(self):
        print("Health:{} End:{} XP:{} Lvl:{} Keys:{} Weapon:{} "
             "Armor:{} Loc:{} Moves:{}".format(self.health, self.endurance,
                 self.xp, self.lvl, self.keys, self.weapon, self.armor,
                 self.location, self.moves))

    # Actions
    def move(self, silent=False):
        self.location = min(roll(keys=self.keys), 9)
        self.moves += 1
        if not silent:
            print("You move onward.")

    # Empty Room/Corridor
    def rest(self):
        self.health_up(1)
        self.endurance_up(3)
        print("You catch some fitful shuteye.")

    def scavenge(self):
        self.health_up(3)
        self.endurance_up(-1)
        print("You forage for food and find some stale bread and tepid water.")

    # Trap Room
    def trigger_trap(self):
        self.health_up(-self.lvl)
        print("You stumble across a trap and trigger it.")

    def disable_trap(self):
        self.endurance_up(-self.lvl)
        print("You spot a trap and take time to carefully disarm it.")

    # Monster Room/Corridor
    def run(self):
        print("You flee in terror.")

    def fight(self):
        self.health_up(-self.lvl)
        self.endurance_up(self.lvl)
        self.xp += self.lvl
        print("You fight valiantly and ", end='')
        if self.health > 0 and self.endurance > 0:
            print("slaughter every monster in the room.")
        else:
            print("fall in battle.")

    # Treasure Room
    def search(self):
        print("You pillage the room of its riches, gaining ", end='')
        if roll(keys=self.keys) <= 3:
            self.keys += 1
            print("a key.")
        else:
            self.xp += self.lvl
            print("{} experience.".format(self.lvl))

    # Stairs Down
    def descend(self):
        self.lvl += 1
        print("You pad cautiously down the stairs.")

    # Boss
    def fightboss(self):
        print("You fight valiantly and ", end='')
        self.health -= 2 * self.lvl
        self.endurance -= 2 * self.lvl
        self.xp += 2 * self.lvl
        if self.health > 0 and self.endurance > 0:
            print("slaughter the beast.")
        else:
            print("fall in battle.")

    # Exit the Dungeon
    def exit(self):
        print("You emerge into freedom!")
        raise GameOverError

    # Game loop
    def loop(self):
        print("You enter a run-down looking dungeon.")
        self.move(silent=True)
        while True:
            self.take_turn()

    def take_turn(self):
        while True:
            self.show_where()
            self.show_stats()
            self.show_prompt()
            what = input("> ").strip().lower()
            try:
                self.action(self.room_actions[self.location][what]['action'])
            except KeyError:
                print("You think about what to do next.")
                continue
            except GameOverError:
                self.new_run()
                self.location = 0
                continue


def main():
    game = Game()
    game.loop()


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    main()
