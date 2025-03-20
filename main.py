import copy
class Player:
    def __init__(self, health,bullets,blanks,gun_state,items, num_adrenaline):
        self.health = health
        self.bullets = bullets
        self.blanks = blanks
        self.gun_state = [-1 for _ in range(bullets+blanks)]
        self.items = items
        self.num_adrenaline = 0 #this item is pretty different
        #gun_state contains all information about the gun available to the player
        #items:
        #0. inverter -flips blank to bullet and vice versa
        #1. burner_phone - gives info about random future bullet
        #2. cigs - heals 1 hp
        #3. jammer - skips apponent's turn
        #4. beer - ejects the bullet
        #5. spyglass - gives info about next bullet
        #6. saw - doubles damage of bullet
        #moves also contain 7 (shoot the gun)
        #and 8 (shoot urselff)
    #hashing, necessary for memoization
    def __hash__(self):
        return hash((self.health, self.bullets, self.blanks, str(self.gun_state), str(self.items), self.num_adrenaline))
    def __eq__(self, other):
        return self.health == other.health and self.bullets == other.bullets and self.blanks == other.blanks and str(self.gun_state) == str(other.gun_state) and str(self.items) == str(other.items) and self.num_adrenaline == other.num_adrenaline

def update_ev(ev, new_ev,to_move):
    if to_move == 1:
        if new_ev[0] > ev[0]:
            return new_ev
        return ev
    if to_move == 1:
        if new_ev[0] < ev[0]:
            return new_ev
        return ev

def evaluate_state(player_a,player_b,gun_state, double_damage,to_move, search_map):
    #evaluate terminal states
    if hash(player_a,player_b,str(gun_state), double_damage,to_move) in search_map:
        return search_map[hash(player_a,player_b,str(gun_state), double_damage,to_move)], None
    if player_a.health <= 0:
        return -1, None
    if player_b.health <= 0:
        return 1, None
    elif player_a.bullets == 0 and player_a.items[0] == 0:
        return 0, None
    #now we actually process the game logic, recursively
    ev = float('-inf') * to_move, None #if to_move is 1, we are maximizing, if -1, we are minimizing
    if to_move == 1:
        #player a is the maximizer, to move
        #we need to try all possible moves, and take the max
        if player_a.items[0] >= 0:
            a_prime = copy.deepcopy(player_a)
            b_prime = copy.deepcopy(player_b)
            a_prime.items[0] -= 1
            if not gun_state[0] ==-1:
                gun_state[0] = 
                ev = max(ev, evaluate_state(a_prime,b_prime,gun_state, double_damage,to_move))
        if player_a.items[1] >= 0:
    

    search_map[hash(player_a,player_b,str(gun_state), double_damage,to_move)] = (ev, best_move)
    return ev, best_move



