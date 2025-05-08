import sys
from math import gcd

directions = {'N': (0,1),
              'NE': (1,1),
              'E': (1,0),
              'SE': (1,-1),
              'S': (0,-1),
              'SW': (-1,-1),
              'W': (-1,0),
              'NW': (-1,1)
              }
dir_order = ['N','NE', 'E','SE','S','SW','W','NW'
             #,'N','NE', 'E','SE','S','SW','W','NW'
             ]
def normalise(x, y): #tried other ways but using gcd seems to be best way of dealing with large ratios
    if x == 0 and y == 0:
        return (0, 0)
    g = gcd(abs(x), abs(y))
    return (x // g, y // g)



def algo(start_dir, players, start_idx):
    #setup
    player_dict = {i:(x,y) for i, (x,y) in enumerate(players)}
    active_players = set(range(len(players)))
    throws = 0
    current_idx, current_dir = start_idx-1, start_dir #adjusts index to be 0-basedm as player_dict is, then +1 at the end to fix this

    while True: #cycle through until reach a player with no passing options (triggers the break)
        cur_x, cur_y = player_dict[current_idx]
        #print((cur_x,cur_y))
        found = False

        start = (dir_order.index(current_dir)+1)%8 #moves direciton clockwise one place

        for dummy in range(8): #we go and check each direction to see if there is a passing option, and then for the first viable direciton we take the closest one
            d=dir_order[(start+dummy)%8]
            dx, dy = directions[d]
            nearest_player = None
            min_dist = float('inf')

            for idx in active_players:
                if idx == current_idx:
                    continue
                px,py = player_dict[idx]
                vec_x,vec_y = px-cur_x,py-cur_y

                if normalise(vec_x, vec_y) == normalise(dx, dy):
                    dist = (vec_x)**2+(vec_y)**2
                    if dist < min_dist:
                        min_dist = dist
                        nearest_player = idx
            
            if nearest_player is not None: #found a player so no need to check other directions, we restart the while loop
                throws+=1
                active_players.remove(current_idx)
                current_idx = nearest_player
                new_start_index = (dir_order.index(d)+4)%8 #reflect direction as player receiving is facing player throwing, deal with the +1 at the beginning of the loop
                current_dir = dir_order[new_start_index]
                found = True
                break
        if not found:
            break
    return throws, current_idx

def main(): #interpreting the input file line by line
    lines = sys.stdin.read().splitlines()
    i = 0
    T = int(lines[i])
    i +=1
    with open("output.txt", "w") as out:
        for _ in range(T):
            N = int(lines[i])
            i += 1
            players = []
            for _ in range(N):
                x,y = map(int, lines[i].split())
                players.append((x,y))
                i +=1
            D = lines[i].strip()
            i+=1
            start_idx = int(lines[i])
            #print(start_idx,D)
            i+=1
            throws,last_player = algo(D,players,start_idx)
            out.write(f"{throws} {last_player+1}\n")
if __name__ == "__main__":
    main()