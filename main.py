import random
from cards import Game, VALID_MOVES, Move, MoveType

g = Game(2)
g.print_full_state()

i = 0
while True:
	m = random.choice(VALID_MOVES)
	player_idx = i % len(g.players)
	i += 1

	if i == 100:
		m = Move(MoveType.KNOCK)
	print(i, m.text_repr(player_idx), "->", g.dump_short_state())
	game_over = g.make_move(m)

	if game_over:
		g.print_full_state(False)
		break
