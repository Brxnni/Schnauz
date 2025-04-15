from enum import Enum, auto
from typing import Self, Union
from string import ascii_uppercase

class Color(Enum):
	CLUBS = auto()
	DIAMONDS = auto()
	HEARTS = auto()
	SPADES = auto()

class Number(Enum):
	SEVEN = auto()
	EIGHT = auto()
	NINE = auto()
	TEN = auto()
	JACK = auto()
	QUEEN = auto()
	KING = auto()
	ACE = auto()

BASE = "\033[38;2;%sm"
GOLD = BASE % "240;140;0"
RED = BASE % "255;15;0"
BLUE = BASE % "0;150;240"
GREEN = BASE % "50;230;110"

BOLD = "\033[1m"
END = "\033[0m"

COLOR_CHARS = {
	"simple": {
		Color.CLUBS:"♣", Color.DIAMONDS:"♦", Color.HEARTS:"♥", Color.SPADES:"♠"
	},
	"colored": {
		Color.CLUBS:f"{BLUE}♣{END}", Color.DIAMONDS:f"{GOLD}♦{END}", Color.HEARTS:f"{RED}♥{END}", Color.SPADES:"♠"
	}
}

NUMBER_CHARS = {
	Number.SEVEN: "7",
	Number.EIGHT: "8",
	Number.NINE: "9",
	Number.TEN: "⏨", # Muss ein Zeichen breit sein
	Number.JACK: "B",
	Number.QUEEN: "D",
	Number.KING: "K",
	Number.ACE: "A"
}

# oop 🖕🖕🖕
class Card:
	def __init__(self, c: Color, n: Number) -> None:
		self.color, self.number = c, n
	def __repr__(self) -> str:
		return COLOR_CHARS["colored"][self.color] + NUMBER_CHARS[self.number]
	def value(self) -> str:
		return {
			Number.SEVEN: 7,
			Number.EIGHT: 8,
			Number.NINE: 9,
			Number.TEN: 10,
			Number.JACK: 10,
			Number.QUEEN: 10,
			Number.KING: 10,
			Number.ACE: 11
		}[self.number]
	def repr_cards(cards: list[Self]) -> str:
		return " ".join([ card.__repr__() for card in cards ])

class MoveType(Enum):
	KNOCK = auto()
	SWAP = auto()
	SWITCH = auto()

class Move:
	def __init__(self, move_type: MoveType, idxs: list[int]=None):
		""" idxs: [ idx within player's cards (0-2), idx within deck (0-2) ] """
		self.type = move_type
		if self.type == MoveType.SWAP: self.idxs = idxs
	def __repr__(self) -> str:
		if self.type == MoveType.KNOCK: return f"<Knock>"
		elif self.type == MoveType.SWITCH: return "<FullDeck>"
		elif self.type == MoveType.SWAP: return f"<Deck[{self.idxs[0]}] <-> Player[{self.idxs[1]}]"
	def text_repr(self, player_index: int) -> str:
		out = repr_player(player_index)
		if self.type == MoveType.SWITCH:
			return out + " tauscht alle seine Karten!"
		elif self.type == MoveType.SWAP:
			# return out + f"tauscht die {BOLD}{self.idxs[1]+1}{END}. Karte des Decks mit seiner {BOLD}{self.idxs[0]+1}{END}. Karte!"
			return out + f" tauscht seine {BOLD}{self.idxs[0]+1}{END}. Karte mit der {BOLD}{self.idxs[1]+1}{END}. Karte des Decks!"
		elif self.type == MoveType.KNOCK:
			return out + " klopft!"

VALID_MOVES = [ Move(MoveType.SWITCH) ] + [ Move(MoveType.SWAP, [i,j]) for i in range(3) for j in range(3) ]

def repr_player(player_idx: int, short: bool=False) -> str:
	if short: return f"{BOLD}{GREEN}{ascii_uppercase[player_idx]}{END}"
	return f"{BOLD}{GREEN}Spieler {ascii_uppercase[player_idx]}{END}"

def player_score(player: list[Card]) -> float:
	# Drei des gleichen Ranges: Spiel endet nicht sofort, hat aber eigenen Wert
	if len(set([ card.number for card in player ])) == 1: return 30.5

	# Farbe mit höchstem Gesamtwert zählt
	colors = [ [ card for card in player if card.color == color ] for color in Color ]
	scores = [ sum([ card.value() for card in color ]) for color in colors ]
	return max(scores)

import random

class Game:
	def __init__(self, player_count: int = 3) -> None:
		self.cards = [ Card(c, n) for c in Color for n in Number ]
		self.players = [ self.draw_cards(3) for _ in range(player_count) ]
		self.deck = self.draw_cards(3)
		self.knocked = None
		self.turn = 0 # Spielerindex

	def draw_cards(self, amount: int) -> list[Card]:
		random.shuffle(self.cards)
		picked = self.cards[-amount:]
		del self.cards[-amount:]
		return picked

	def print_full_state(self, compact: bool=True) -> None:
		if compact:
			print(Card.repr_cards(self.deck) + f"{BOLD}   |   {END}" + " ".join([ f"{repr_player(i, True)}: {END}" + Card.repr_cards(player) for i, player in enumerate(self.players) ]))
			return

		print(BOLD + GREEN + "             Deck" + END)
		print(f"           {Card.repr_cards(self.deck)}")
		print(f"\n              {BOLD}↑↓{END}\n")
		print(" | ".join([ Card.repr_cards(player) for player in self.players ]))
		print("    " + "          ".join([ repr_player(i, True) for i in range(len(self.players)) ]) + END)

	def dump_short_state(self) -> str:
		return Card.repr_cards(self.deck)

	def make_move(self, move: Move) -> bool:
		"""-> bool: gewonnen?"""
		# Zug machen
		if move.type == MoveType.SWAP:
			self.players[self.turn][move.idxs[0]], self.deck[move.idxs[1]] = \
				self.deck[move.idxs[1]], self.players[self.turn][move.idxs[0]]
		elif move.type == MoveType.SWITCH:
			self.players[self.turn], self.deck = \
				self.deck, self.players[self.turn]
		elif move.type == MoveType.KNOCK:
			self.knocked = self.turn

		# Win conditions für Spieler überprüfen
		# Feuer (= nur Asse) oder 31
		if all([ card.number == Number.ACE for card in self.players[self.turn] ]) or \
		player_score(self.players[self.turn]) == 31:
			self.over = True
			print(f"{repr_player(self.turn)} hat gewonnen!")
			return True

		if self.knocked != None:
			if self.turn == (self.knocked - 1) % len(self.players):
				print(f"Nach dem Klopfen war jeder ein Mal dran.")
				scores = [ (idx, player_score(player)) for idx, player in enumerate(self.players) ]
				scores.sort(key=lambda p:p[1], reverse=True)
				print(f"{repr_player(scores[0][0])} gewinnt mit {scores[0][1]} Punkten!")
				return True

		self.turn = (self.turn + 1) % len(self.players)
		return False
