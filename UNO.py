import random
import pickle
import os
from IPython.display import clear_output

class UNOCard:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __str__(self):
        return f"{self.color} {self.value}"

    def __repr__(self):
        return self.__str__()

    def matches(self, card):
        return (self.color == card.color or self.value == card.value) or self.color == "Wild"

class UNODeck:
    def __init__(self):
        colors = ["Red", "Yellow", "Green", "Blue"]
        values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Skip", "Reverse", "Draw Two"]

        self.deck = [UNOCard(color, value) for color in colors for value in values] + [UNOCard(color, value) for color in colors for value in values[1:]]

        self.deck += [UNOCard("Wild", "Wild") for _ in range(4)]
        self.deck += [UNOCard("Wild", "Draw Four") for _ in range(4)]

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self, num_players, num_cards):
        hands = [[] for _ in range(num_players)]
        for i in range(num_cards):
            for hand in hands:
                hand.append(self.draw())
        return hands

    def draw(self):
        if len(self.deck) == 0:
            raise Exception("Deck is empty")
        return self.deck.pop()

    def __str__(self):
        return str(self.deck)

    def __repr__(self):
        return self.__str__()

class UNOPlayer:

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0

    def __str__(self):
        hand_str = '\n'.join([f"{i+1}. {card}" for i, card in enumerate(self.hand)])
        return f"{self.name}:\n{hand_str}"

    def __repr__(self):
        return self.__str__()

    def play(self, card):
        if card not in self.hand:
            raise Exception(f"Card {card} not in hand")
        self.hand.remove(card)
        return card

    def draw(self, card):
        self.hand.append(card)

    def has_won(self):
        return len(self.hand) == 0


class UNOGame:
    
    def __init__(self, players, starting_cards=7, score_limit=None):
        self.players = players
        self.starting_cards = starting_cards
        self.score_limit = score_limit
        self.deck = UNODeck()
        self.deck.shuffle()
        self.discard_pile = []
        self.current_player = 0
        self.direction = 1

    def start_game(self):
        hands = self.deck.deal(len(self.players), self.starting_cards)
        for player, hand in zip(self.players, hands):
            player.hand = hand
        first_card = self.deck.draw()
        while first_card.value in ["Skip", "Reverse", "Draw Two", "Draw Four", "Wild"]:
            self.deck.deck.append(first_card)
            self.deck.shuffle()
            first_card = self.deck.draw()
        self.discard_pile.append(first_card)

    def save_game(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load_game(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)

    def next_player(self):
        self.current_player = (self.current_player + self.direction) % len(self.players)


    def play_card(self, card_index, chosen_color=None):
        player = self.players[self.current_player]
        if card_index < 0 or card_index >= len(player.hand):
            raise Exception(f"Invalid card index: {card_index}")
        card = player.hand[card_index]
        if card.matches(self.discard_pile[-1]):
            player.play(card)
            print(f"{player.name} played {card}")
            if card.color == "Wild":
                if chosen_color is None:
                    raise Exception("Must choose a color when playing a Wild card")
                if chosen_color not in ["Red", "Yellow", "Green", "Blue"]:
                    raise Exception(f"Invalid color choice: {chosen_color}")
                card.color = chosen_color
                print(f"{player.name} chose {chosen_color}")
            self.discard_pile.append(card)
            if card.value == "Reverse":
                self.direction *= -1
            elif card.value == "Skip":
                self.next_player()
            elif card.value == "Draw Two":
                self.next_player()
                player = self.players[self.current_player]
                player.draw(self.deck.draw())
                player.draw(self.deck.draw())
            elif card.value == "Draw Four":
                self.next_player()
                player = self.players[self.current_player]
                challenge = input(f"{player.name}, do you want to challenge the Wild Draw 4? (y/n): ")
                if challenge == 'y':
                    prev_card = self.discard_pile[-2]
                    if any(c.color == prev_card.color for c in player.hand):
                        print("Challenge successful")
                        for dc in range(4):
                            player.draw(self.deck.draw())
                    else:
                        print("Challenge unsuccessful")
                        for _ in range(6):
                            player.draw(self.deck.draw())
                else:
                    for _ in range(4):
                        player.draw(self.deck.draw())
            self.next_player()
            self.next_player()
            return True
        raise Exception(f"Card {card} does not match top of discard pile")


    def draw_card(self):
        player = self.players[self.current_player]
        try:
            player.draw(self.deck.draw())
        except Exception as e:
            print(e)
            print("Reshuffling discard pile into deck")
            top_card = self.discard_pile.pop()
            self.deck.deck = self.discard_pile
            self.discard_pile = [top_card]
            random.shuffle(self.deck.deck)
            player.draw(self.deck.draw())

    def check_winner(self):
        for player in self.players:
            if player.has_won():
                return player
        return None


class UNOGameController:
    def __init__(self):
        pass
    
    def get_action(self):
        actions = ["New game", "Load game"]
        for i, action in enumerate(actions):
            print(f"{i+1}. {action}")
        action_index = int(input("Choose an action: ")) - 1
        if action_index < 0 or action_index >= len(actions):
            print("Invalid choice")
            return self.get_action()
        os.system('cls' if os.name == 'nt' else 'clear')
        return actions[action_index].lower()
    
    def start_new_game(self):
        num_players = int(input("Enter number of players: "))
        players = []
        for i in range(num_players):
            name = input(f"Enter name of player {i+1}: ")
            players.append(UNOPlayer(name))
        os.system('cls' if os.name == 'nt' else 'clear')
        starting_cards = int(input("Enter number of starting cards: "))
        score_limit_input = input("Enter score limit (leave blank for no limit): ")
        score_limit = int(score_limit_input) if score_limit_input != "" else None
        game = UNOGame(players, starting_cards=starting_cards, score_limit=score_limit)
        game.start_game()
        os.system('cls' if os.name == 'nt' else 'clear')
        return game
    
    
    def save_current_game_state(self, game):
        print("Save current game state")
        print("1. Save to new file")
        print("2. Overwrite existing save")
        choice = int(input("Enter your choice: "))
        if choice == 1:
            filename = input("Enter filename for new save: ")
            if not filename.endswith('.pkl'):
                filename += '.pkl'
            game.save_game(filename)
            print(f"Game saved to {filename}")
        elif choice == 2:
            saved_games = [filename for filename in os.listdir() if filename.endswith('.pkl')]
            if not saved_games:
                print("No saved games found")
                return
            print("Saved games:")
            for i, filename in enumerate(saved_games):
                print(f"{i+1}. {filename}")
            index = int(input("Enter the index of the saved game to overwrite: ")) - 1
            filename = saved_games[index]
            game.save_game(filename)
            print(f"Game saved to {filename}")


    def load_saved_game(self):
        print("Saved games:")
        saved_games = [filename for filename in os.listdir() if filename.endswith('.pkl')]
        for i, filename in enumerate(saved_games):
            print(f"{i+1}. {filename}")
        index = int(input("Enter the index of the saved game to load: ")) - 1
        filename = saved_games[index]
        game = UNOGame.load_game(filename)
        return game
    
    def display_game_state(self, game):
        print("=================================================")
        print(f"Top of discard pile: {game.discard_pile[-1]}")
        print("=================================================")
        current_player = game.players[game.current_player]
        for player in game.players:
            if player != current_player:
                print(f"Name: {player.name}")
                print(f"No of Cards in hand: {len(player.hand)}")
                if player.score > 0:
                    print(f"Score: {player.score}")
            else:
                print(f"\n{current_player.name}'s turn: ")
                hand_str = '\n'.join([f"{i+1}. {card}" for i, card in enumerate(current_player.hand)])
                print(f"\n{hand_str}")
                print(" ")
            print("------------------------")
    
    def get_player_action(self, current_player):
        actions = ["Play card", "Draw card", "Quit game"]
        for i, action in enumerate(actions):
            print(f"{i+1}. {action}")
        action_index = int(input("Choose an action: ")) - 1
        if action_index < 0 or action_index >= len(actions):
            print("Invalid choice")
            return self.get_player_action(current_player)
        return actions[action_index].lower().replace(' ', '_')

    
    def draw_card(self, game, current_player): 
       try: 
           game.draw_card() 
           print(f"{current_player.name} drew a card") 
       except Exception as e:
           print(e) 
           print("Reshuffling discard pile into deck")
           top_card = game.discard_pile.pop() 
           game.deck.deck = game.discard_pile 
           game.discard_pile = [top_card] 
           random.shuffle(game.deck.deck) 
           current_player.draw(game.deck.draw()) 

    def calculate_score(self, player):
        score = 0
        for card in player.hand:
            if card.value.isdigit():
                score += int(card.value)
            elif card.value in ["Skip", "Reverse", "Draw Two"]:
                score += 20
            elif card.value == "Wild" or card.value == "Draw Four":
                score += 50
        return score
        
    def quit_game(self, game, current_player):
        votes = 0
        for player in game.players:
            if player != current_player:
                vote = input(f"{player.name}, do you agree to quit the game? (y/n): ")
                if vote == 'y':
                    votes += 1
        if votes >= len(game.players) // 2:
            save = input("Do you wnat to save the game Y/N: ").upper()
            if save == 'Y':
                self.save_current_game_state(game)
                return True
            else:
                print("Game ended")
                scores = [(player.name, self.calculate_score(player)) for player in game.players]
                scores.sort(key=lambda x: x[1])
                print("Final scores:")
                for name, score in scores:
                    print(f"{name}: {score}")
                winner = scores[0][0]
                self.display_winner(winner)
                return True
        else:
            print("Not enough votes to quit the game")
    
    def display_winner(self,winner):
      print(f"\n{winner[0][0][0]} wins!")
    
    def play_card(self, game, current_player):
        try:
            card_index_input=input("Enter index of card to play (or '0' to cancel): ")
            if(card_index_input=='0'):
                return
            else:
                try:
                    card_index=int(card_index_input) - 1
                except ValueError as e:
                    print(e)
                    return
            chosen_color=None
            if current_player.hand[card_index].color=="Wild":
                colors = ["Red", "Yellow", "Green", "Blue"]
                for i, color in enumerate(colors):
                    print(f"{i+1}. {color}")
                color_index = int(input("Choose a color: ")) - 1
                if color_index < 0 or color_index >= len(colors):
                    print("Invalid choice")
                    return self.play_card(game,current_player)
                chosen_color=colors[color_index]
            game.play_card(card_index,chosen_color)
            winner=game.check_winner()
            if winner is not None:
                self.display_winner(winner)
                return True
            os.system('cls' if os.name == 'nt' else 'clear')
            game.next_player()
        except Exception as e:
            print(e)
        

def play_game():
    controller = UNOGameController()
    action = controller.get_action()
    if action == 'new game':
      game = controller.start_new_game()
      
    elif action == 'load game':
      game = controller.load_saved_game()
    
    while True:
        current_player = game.players[game.current_player]
        controller.display_game_state(game)
        action=controller.get_player_action(current_player)
        
        if action == 'play_card':
            result=controller.play_card(game, current_player)
            if result==True:
                break
            game.next_player()
        
        elif action == 'draw_card':
            controller.draw_card(game, current_player)
            game.next_player()

        elif action == 'quit_game':
            result=controller.quit_game(game, current_player)
            if result==True:      
                break
        os.system('cls' if os.name == 'nt' else 'clear')

    
play_game()