import copy
class Player:
    def __init__(self, health,bullets,blanks,gun_state,items, num_adrenaline):
        self.health = health
        self.bullets = bullets
        self.blanks = blanks
        self.gun_state = [-1 for _ in range(bullets+blanks)]
        self.items = items
        self.num_adrenaline = 0 #this item is pretty different
        self.jammed = False
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
        return hash((self.health, self.bullets, self.blanks, str(self.gun_state), str(self.items), self.num_adrenaline, self.jammed))
    def __eq__(self, other):
        return self.health == other.health and self.bullets == other.bullets and self.blanks == other.blanks and str(self.gun_state) == str(other.gun_state) and str(self.items) == str(other.items) and self.num_adrenaline == other.num_adrenaline and self.jammed == other.jammed

def update_ev(ev, new_ev,to_move):
    if to_move == 0:
        if new_ev > ev:
            return new_ev
        return ev
    if to_move == 1:
        if new_ev < ev:
            return new_ev
        return ev

def evaluate_state(player_a,player_b,gun_state, double_damage,to_move, search_map):
    #transposition table
    if hash(player_a,player_b,str(gun_state), double_damage,to_move) in search_map:
        return search_map[hash(player_a,player_b,str(gun_state), double_damage,to_move)]
    #evaluate terminal states, tuning this with self-play should build the optimal strategy
    if player_a.health <= 0:
        return -1
    if player_b.health <= 0:
        return 1
    elif player_a.bullets == 0 and player_a.items[0] == 0:
        return 0
    #now we actually process the game logic, recursively
    ev = float('-inf') if to_move ==0 else float('inf') #if to_move is 0, we are maximizing, if 1, we are minimizing
    check = player_a if to_move == 0 else player_b
    if check.items[0] >= 0:
        a_prime = copy.deepcopy(player_a)
        b_prime = copy.deepcopy(player_b)
        if to_move == 0:
            a_prime.items[0] -= 1
        else:
            b_prime.items[0] -= 1
        if not gun_state[0] ==-1:
            gun_state[0] = (gun_state[0] + 1) % 2
            a_prime.gun_state[0] = a_prime.gun_state[0] if a_prime.gun_state[0] == -1 else gun_state[0]
            b_prime.gun_state[0] = b_prime.gun_state[0] if b_prime.gun_state[0] == -1 else gun_state[0]
            a_prime.bullets = b_prime.blanks
            a_prime.blanks = b_prime.bullets
            b_prime.bullets = a_prime.blanks
            b_prime.blanks = a_prime.bullets
            ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state, double_damage,to_move,search_map), to_move)
        else:
            a_prime.bullets = b_prime.blanks
            a_prime.blanks = b_prime.bullets
            b_prime.bullets = a_prime.bullets
            b_prime.blanks = a_prime.blanks
            ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state, double_damage,to_move,search_map), to_move)
    if check.items[1] >= 0:
        a_prime = copy.deepcopy(player_a)
        b_prime = copy.deepcopy(player_b)
        if to_move == 0:
            a_prime.items[1] -= 1
        else:
            b_prime.items[1] -= 1
    

    search_map[hash(player_a,player_b,str(gun_state), double_damage,to_move)] = ev
    return ev



