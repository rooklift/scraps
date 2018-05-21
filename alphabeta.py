# Adapted from http://rin.io/chess-engine/

def alphaBetaMax(position, alpha, beta, depth):
	if depth <= 0:
		return position.evaluate()
	for c in position.children():
		score = alphaBetaMin(c, alpha, beta, depth - 1)
		if score >= beta:
			return beta			# fail hard beta-cutoff
		if score > alpha:
			alpha = score		# alpha acts like max in MiniMax
	return alpha

def alphaBetaMin(position, alpha, beta, depth):
	if depth <= 0:
		return position.evaluate() * -1
	for c in position.children():
		score = alphaBetaMax(c, alpha, beta, depth - 1)
		if score <= alpha:
			return alpha		# fail hard alpha-cutoff
		if score < beta:
			beta = score		# beta acts like min in MiniMax
	return beta

score = alphaBetaMax(position, -inf, +inf, depth)
