import copy
from numpy import random
from joblib import Parallel, delayed
class Player:
    def __init__(self, health,bullets,blanks,items, num_adrenaline):
        self.health = health
        self.bullets = bullets
        self.blanks = blanks
        self.gun_state = [-1 for _ in range(bullets+blanks)]
        self.items = items
        self.num_adrenaline = num_adrenaline #this item is pretty different
        self.jammed = False
        #gun_state contains all information about the gun available to the player
        #items:
        #0. inverter -flips blank to bullet and vice versa
        #1. saw - doubles damage of bullet
        #2. cigs - heals 1 hp
        #3. jammer - skips apponent's turn
        #4. beer - ejects the bullet
        #5. spyglass - gives info about next bullet
        #6. burner_phone - gives info about random future bullet
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

def evaluate_state(player_a,player_b,gun_state,max_health, double_damage,to_move, search_map):
    #transposition table
    if hash(player_a,player_b,str(gun_state), max_health, double_damage,to_move) in search_map:
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
    if check.jammed:
        return evaluate_state(player_a,player_b,gun_state, max_health, double_damage,(to_move+1)%2,search_map)
    if check.items[0] > 0: #inverter
        a_prime = copy.deepcopy(player_a)
        b_prime = copy.deepcopy(player_b)
        gun_state_prime = copy.deepcopy(gun_state)
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
            ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, double_damage,to_move,search_map), to_move)
        else:
            a_prime.bullets = b_prime.blanks
            a_prime.blanks = b_prime.bullets
            b_prime.bullets = a_prime.bullets
            b_prime.blanks = a_prime.blanks
            ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, double_damage,to_move,search_map), to_move)
    if check.items[1] > 0: #saw
        a_prime = copy.deepcopy(player_a)
        b_prime = copy.deepcopy(player_b)
        gun_state_prime = copy.deepcopy(gun_state)
        if to_move == 0:
            a_prime.items[1] -= 1
        else:
            b_prime.items[1] -= 1
        ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, max_health, 2,to_move,search_map), to_move)
    if check.items[2] >= 0: #cigs
        a_prime = copy.deepcopy(player_a)
        b_prime = copy.deepcopy(player_b)
        gun_state_prime = copy.deepcopy(gun_state)
        if to_move == 0:
            a_prime.items[2] -= 1
            if a_prime.health < max_health:
                a_prime.health += 1
        else:
            b_prime.items[2] -= 1
            if b_prime.health < max_health:
                b_prime.health += 1
        ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, max_health, double_damage,to_move,search_map), to_move)
    if check.items[3] > 0: #jammer
        a_prime = copy.deepcopy(player_a)
        b_prime = copy.deepcopy(player_b)
        gun_state_prime = copy.deepcopy(gun_state)
        if to_move == 0:
            a_prime.items[3] -= 1
            b_prime.jammed = True
        else:
            b_prime.items[3] -= 1
            a_prime.jammed = True
        ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, max_health, double_damage,to_move,search_map), to_move)
    if check.items[4] > 0: #beer
        a_prime = copy.deepcopy(player_a)
        b_prime = copy.deepcopy(player_b)
        gun_state_prime = copy.deepcopy(gun_state)
        if to_move == 0:
            a_prime.items[4] -= 1
        else:
            b_prime.items[4] -= 1
        if not gun_state_prime[0] == -1:
            bullet = gun_state_prime.pop(0)
            a_prime.gun_state.pop(0)
            b_prime.gun_state.pop(0)
            a_prime.bullets -= bullet
            b_prime.bullets -= bullet
            a_prime.blanks -= (1-bullet)
            b_prime.blanks -= (1-bullet)
        else:
            bullet = 1 if random.randint(len(gun_state)) < a_prime.bullets else 0
            a_prime.bullets -= bullet
            b_prime.bullets -= bullet
            a_prime.blanks -= (1-bullet)
            b_prime.blanks -= (1-bullet)
            gun_state_prime.pop(0)
            a_prime.gun_state.pop(0)
            b_prime.gun_state.pop(0)
            ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, max_health, double_damage,to_move,search_map), to_move)
    if check.items[5] > 0: #spyglass
        a_prime = copy.deepcopy(player_a)
        b_prime = copy.deepcopy(player_b)
        gun_state_prime = copy.deepcopy(gun_state)
        if gun_state_prime[0] == -1:
                gun_state_prime[0] = 1 if random.randint(len(gun_state_prime)) < a_prime.bullets else 0
        if to_move == 0:
            a_prime.items[5] -= 1
            a_prime.gun_state[0] = gun_state_prime[0]

        else:
            b_prime.items[5] -= 1
            b_prime.gun_state[0] = gun_state_prime[0]
        ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, max_health, double_damage,to_move,search_map), to_move)
    if check.items[6] >= 0: #burner phone
        a_prime = copy.deepcopy(player_a)
        b_prime = copy.deepcopy(player_b)
        gun_state_prime = copy.deepcopy(gun_state)
        if len(gun_state_prime) > 1:
            indices = [i for i in range(len(gun_state_prime)) if check.gun_state[i] == -1]
            if 0 in indices:
                indices.remove(0)
        else:
            indices = [0]
        index = random.choice(indices)
        if gun_state_prime[index] == -1:
                gun_state_prime[index] = 1 if random.randint(len(gun_state_prime)) < a_prime.bullets else 0
        if to_move == 0:
            a_prime.items[index] -= 1
            a_prime.gun_state[index] = gun_state_prime[index]
        else:
            b_prime.items[index] -= 1
            b_prime.gun_state[index] = gun_state_prime[index]
        ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, max_health, double_damage,to_move,search_map), to_move)
    #TODO IMPLEMENT ADRENALINE
    #now we handle the shooting logic

    #shoot enemy
    a_prime = copy.deepcopy(player_a)
    b_prime = copy.deepcopy(player_b)
    gun_state_prime = copy.deepcopy(gun_state)
    if gun_state_prime[0] == -1:
        gun_state_prime[0] = 1 if random.randint(len(gun_state_prime)) < a_prime.bullets else 0
    bullet = gun_state_prime.pop(0)
    a_prime.gun_state.pop(0)
    b_prime.gun_state.pop(0)
    a_prime.bullets -= bullet
    b_prime.bullets -= bullet
    a_prime.blanks -= (1-bullet)
    b_prime.blanks -= (1-bullet)
    if to_move == 0:
        b_prime.health -= bullet * double_damage
    else:
        a_prime.health -= bullet * double_damage
    ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, max_health, 1,(to_move+1)%2,search_map), to_move)
    #shoot self
    a_prime = copy.deepcopy(player_a)
    b_prime = copy.deepcopy(player_b)
    gun_state_prime = copy.deepcopy(gun_state)
    if gun_state_prime[0] == -1:
        gun_state_prime[0] = 1 if random.randint(len(gun_state_prime)) < a_prime.bullets else 0
    bullet = gun_state_prime.pop(0)
    a_prime.gun_state.pop(0)
    b_prime.gun_state.pop(0)
    a_prime.bullets -= bullet
    b_prime.bullets -= bullet
    a_prime.blanks -= (1-bullet)
    b_prime.blanks -= (1-bullet)
    if to_move == 0:
        a_prime.health -= bullet * double_damage
    else:
        b_prime.health -= bullet * double_damage
    ev = update_ev(ev, evaluate_state(a_prime,b_prime,gun_state_prime, max_health, 1,(to_move+bullet)%2,search_map), to_move)
    search_map[hash(player_a,player_b,str(gun_state), double_damage,to_move)] = ev
    return ev

def avg_ev(player_a,player_b,gun_state,max_health,double_damage,num_games):
    ev = 0
    #use joblib to parallelize the evaluation
    evs = Parallel(n_jobs=-1)(delayed(evaluate_state)(player_a,player_b,gun_state,max_health,double_damage,0,{}) for _ in range(num_games))
    return sum(evs)/num_games

if __name__ == "__main__":
    num_bullets =3
    num_blanks = 3
    a_hp = 10
    b_hp = 10
    a_items = [
        0, #inverter
        0, #saw
        0, #cigs
        0, #jammer
        0, #beer    
        0, #spyglass
        0 #burner phone
        ]
    b_items = [
        0, #inverter
        0, #saw
        0, #cigs
        0, #jammer
        0, #beer
        0, #spyglass
        0 #burner phone
        ]

    player_a = Player(a_hp,num_bullets,num_blanks, a_items,0)
    player_b = Player(b_hp,num_bullets,num_blanks, b_items,0)
    gun_state = [-1 for _ in range(num_bullets+num_blanks)]
    print(avg_ev(player_a,player_b,gun_state,10,2,1))
