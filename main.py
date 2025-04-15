import random
from cards import Card, Game, VALID_MOVES

g = Game()
g.print_full_state()

i = 0
while True:
	m = random.choice(VALID_MOVES)
	player_idx = i % 3
	i += 1

	g.make_move(player_idx, m)
	print(i, m.text_repr(player_idx), "->", Card.repr_cards(g.deck))
	has_won = g.has_won()
	if has_won:
		print(f"Spieler {has_won} hat gewonnen!!")
		g.print_full_state(False)
		break
