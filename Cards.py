import random
random.seed(4)

deck = []

for suits in ["diamonds", "clubs", "hearts", "spades"]:
	for rank in ["ace",1,2,3,4,5,6,7,8,9,10,"jack", "queen", "king"]:
		deck.append("%s of %s" % (rank, suits))

random.shuffle(deck)
while len(deck) > 0:
	card = deck.pop()
	print(card)