import random


# TODO: сделать нормальный рандом с уходом карт из колоды.
def create_card():
    """
    returns card name:string
    """
    cards = ['two','three','four','five','six','seven','eight','nine','ten','jack','queen','king','ace']
    
    card_num = random.randint(1,13)
    
    card = cards[card_num-1]
    
    print(f"new card - {card}")
    return card

# for i in range(111):
#     print(create_card())
