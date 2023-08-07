import random

#  x ---->
# y 8 1 2
# | 7 * 3
# | 6 5 4
# v
NAVGRID = """    ^ 
  8 1 2
< 7 * 3 >
  6 5 4
    v
"""
NAV_DIRECTIONS = (
    None,  # 0
    (0, -1),  # 1
    (1, -1),  # 2
    (1, 0),  # 3
    (1, 1),  # 4
    (0, 1),  # 5
    (-1, 1),  # 6
    (-1, 0),  # 7
    (-1, -1),  # 8
)

TIME_LIMIT = 30

CIV_NAME = "Ilsodil"


class entity:
    DWARF = 0
    GOBLIN = 1
    HUMAN = 2
    ELF = 3  # not implemented >:)

    NAMES = ["dwarf", "goblin", "human", "elf"]


class weapon:
    RAILGUN = 0
    MAGMA = 1
    ARBALEST = 2
    NAMES = ["adamantine railgun", "magma cannon", "plasma catapult"]


def dist(p1, p2):
    return ((p1[0] -
             p2[0]) ** 2 +
            (p1[1] -
             p2[1]) ** 2) \
           ** (1 / 2)


class Galaxy():
    def __init__(self, starmap=None, starmap_size=(6, 4), sector_size=(10, 10)):
        # starmap represents 6x * 4y grid, but is dictionary of sector designations.
        self.starmap = starmap
        self.STARMAP_WIDTH, self.STARMAP_HEIGHT = starmap_size
        self.SECTOR_WIDTH, self.SECTOR_HEIGHT = sector_size
        self.stardate = 0

    def gen_starmap(self, num_stars, num_goblins, num_stations):
        # print("populating parent_galaxy...")
        self.starmap = {}
        for i in list('abcdefghijklmnopqrstuvwx'):
            self.starmap[i] = [[None for i in range(10)] for j in range(10)]
        # place stars
        for i in range(num_stars):
            # print("starting placement of star", i)
            s_designation = random.choice(list(self.starmap.keys()))
            s = self.starmap[s_designation]
            local_coords = [random.randint(0, 9), random.randint(0, 9)]
            placed = False
            while not placed:
                if s[local_coords[0]][local_coords[1]] != None:
                    # print("tile occupied by", s[local_coords[0]][local_coords[1]])
                    local_coords = [random.randint(0, 9), random.randint(0, 9)]
                elif s[local_coords[0]][local_coords[1]] == None:
                    # print("placing star", i, "in sector", s_designation, "at", local_coords)
                    s[local_coords[0]][local_coords[1]] = Star()
                    placed = True
        # place stations
        for i in range(num_stations):
            # print("starting placement of station", i)
            s_designation = random.choice(list(self.starmap.keys()))
            s = self.starmap[s_designation]
            local_coords = [random.randint(0, 9), random.randint(0, 9)]
            placed = False
            while not placed:
                if s[local_coords[0]][local_coords[1]] != None:
                    # print("tile occupied by", s[local_coords[0]][local_coords[1]])
                    local_coords = [random.randint(0, 9), random.randint(0, 9)]
                elif s[local_coords[0]][local_coords[1]] == None:
                    # print("placing station", i, "in sector", s_designation, "at", local_coords)
                    s[local_coords[0]][local_coords[1]] = Station()
                    placed = True
        # place goblins!
        for i in range(num_goblins):
            # print("starting placement of goblins", i)
            s_designation = random.choice(list(self.starmap.keys()))
            s = self.starmap[s_designation]
            local_coords = [random.randint(0, 9), random.randint(0, 9)]
            placed = False
            while not placed:
                if s[local_coords[0]][local_coords[1]] != None:
                    # print("tile occupied by", s[local_coords[0]][local_coords[1]])
                    local_coords = [random.randint(0, 9), random.randint(0, 9)]
                elif s[local_coords[0]][local_coords[1]] == None:
                    # print("placing goblin", i, "in sector", s_designation, "at", local_coords)
                    s[local_coords[0]][local_coords[1]] = Ship("newship" + str(i), parent_entity=entity.GOBLIN,
                                                               sector=s_designation, weapons=[weapon.ARBALEST, weapon.ARBALEST],
                                                               coords=[local_coords[1],local_coords[0]], energy=random.randint(1,2), ammo=100, parent_galaxy=self)
                    placed = True

    def set_tile(self, sector, x, y, object, replace=False):
        # returns True on success
        if not replace and self.starmap[sector][y][x] != None:  # row-column!
            return False
        #print(f"setting {self.starmap[sector][y][x]} at {(x, y)} to {object}")
        self.starmap[sector][y][x] = object
        return True

    def get_tile(self, sector, x, y):
        row, col = y, x
        return self.starmap[sector][row][col]

    def clear_tile(self, sector, x, y):
        if self.valid_coords(sector, x, y):
            self.starmap[y][x] = None

    def count_objects(self, s_designation, ignore_player = True):
        # returns STARs, STATIONs, SHIPs
        sector = self.starmap[s_designation]
        star_count = 0
        station_count = 0
        ship_count = 0
        for row in sector:
            for tile in row:
                if isinstance(tile, Star):
                    star_count += 1
                elif isinstance(tile, Station):
                    station_count += 1
                elif isinstance(tile, Ship):
                    ship_count += 1 - (ignore_player*tile.parent_entity==entity.DWARF)
        return [star_count, station_count, ship_count]

    def get_objects(self, s_designation):
        # returns stars, stations, ships
        objects = [[], [], []]
        sector = self.starmap[s_designation]
        for row in sector:
            for tile in row:
                if isinstance(tile, Star):
                    objects[0].append(tile)
                elif isinstance(tile, Station):
                    objects[1].append(tile)
                elif isinstance(tile, Ship):
                    objects[2].append(tile)
                    print(f"added {tile}, {entity.NAMES[tile.parent_entity]} in {tile.sector}")
        return objects

    def sector_from_designation(self, s_designation):
        return self.starmap[s_designation]

    def designation_from_sector_coords(self, x, y):
        numeric = x % self.STARMAP_WIDTH + y * self.STARMAP_WIDTH
        return list(self.starmap.keys())[numeric]

    def sector_coords_from_designation(self, s_designation):
        key = list('abcdefghijklmnopqrstuvwx').index(s_designation)
        # print(f"sector {s_designation} is at index {key}")
        row = int(key / (self.STARMAP_HEIGHT + 2))
        col = key - (row * self.STARMAP_WIDTH)
        return col, row  # x, y

    def valid_coords(self, sector, x, y):
        return sector in self.starmap.keys() \
                and 0 <= x < self.SECTOR_WIDTH \
                and 0 <= y < self.SECTOR_HEIGHT \
                and int(x) == x and int(y) == y

    def set_player(self, player):
        self.player = player

    def tick(self, stardates):
        for i in range(stardates):
            for ship in self.get_objects(self.player.sector)[2]:
                ship.tick()
            self.stardate += 1

    def neighbors(self, sector, x, y, orthogonal=False):
        neighbors = []
        deltas = [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1), (0, -1), (0, 1)] \
            if not orthogonal \
            else [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for delta in deltas:
            n_coords = x + delta[0], y + delta[1]
            n_coords = max(n_coords[0], 0), max(n_coords[1], 0)
            n_coords = min(n_coords[0], self.SECTOR_WIDTH), min(n_coords[1], self.SECTOR_HEIGHT)
            # print(f"checking neighbor at {n_coords}")
            try:
                n = self.get_tile(sector, *n_coords)
                neighbors.append(n)
            except:
                pass

        return neighbors

    def cast(self, sector, start, slope, first = True):
        path = []
        current = start[0] + slope[0], start[1] + slope[1]
        #print(f"cast on {current}")
        while self.valid_coords(sector, *current):
            new_tile = self.get_tile(sector, *current)
            #print(f"path: {new_tile} at {current}")
            if first and new_tile != None: return new_tile
            path.append(new_tile)
            current = [current[i] + slope[i] for i in range(len(current))]
        return path





class Ship():
    MAX_ENERGY = 1000
    MAX_AMMO = 20
    MAX_HULL = 100

    def __init__(self, name, parent_entity, sector, coords, weapons, energy, ammo, parent_galaxy: Galaxy):
        self.name = name
        self.parent_entity = parent_entity
        self.sector = sector
        self.x, self.y = coords
        self.energy = energy
        self.weapons = weapons
        self.ammo = ammo
        self.parent_galaxy = parent_galaxy
        self.hull = 100
        self.shields = 0

    def get_char(self):
        return ("@", "g", "e")[self.parent_entity]

    def move(self, dx, dy):
        try:
            new_sector_x, new_sector_y = int(dx / self.parent_galaxy.SECTOR_WIDTH) + \
                                         self.parent_galaxy.sector_coords_from_designation(self.sector)[0], int(
                dy / self.parent_galaxy.SECTOR_HEIGHT) + self.parent_galaxy.sector_coords_from_designation(self.sector)[
                                             1]
            new_sector = self.parent_galaxy.designation_from_sector_coords(new_sector_x, new_sector_y)
            new_x, new_y = (self.x + dx) % self.parent_galaxy.SECTOR_WIDTH, (
                        self.y + dy) % self.parent_galaxy.SECTOR_HEIGHT
            return (new_sector, new_x, new_y)
        except IndexError:
            return None

    def move_to(self, new_sector, new_x, new_y, clamp = True):
        if clamp:
            new_x = max(0, new_x)
            new_x = min(new_x, self.parent_galaxy.SECTOR_WIDTH - 1)
            new_y = max(0, new_y)
            new_y = min(new_y, self.parent_galaxy.SECTOR_HEIGHT - 1)
        #print(f" {self.name} moving to {(new_x, new_y)}")
        self.parent_galaxy.set_tile(self.sector, self.x, self.y, None, True)  # clear current tile

        self.sector = new_sector
        self.x = new_x
        self.y = new_y

        self.parent_galaxy.set_tile(self.sector, self.x, self.y, self, False)  # add to destination tile

    def tick(self):
        #TODO: AI vessels should actually move on grid. fix bug and implement energy
        #print(f"vessel {self.name} tick called")
        if self.parent_entity == entity.GOBLIN:
            self.energy = [2, 0, 1][self.energy]  # cycle thru energy
            if self.energy == 2:
                try:
                    dx, dy = [random.randint(-3, 3), random.randint(-3, 3)]
                    newx, newy = self.x + dx, self.y + dy
                    self.move_to(self.sector, newx, newy)
                    print(f"goblin moving to {(self.x, self.y)}")
                except Exception as e:
                    print(" "+str(e))
            elif self.energy == 1:
                vessels = self.parent_galaxy.get_objects(self.sector)[2]
                print(f"goblin sees: {list(v.parent_entity for v in vessels)}")
                dwarf = list(filter(lambda v: v.parent_entity == entity.DWARF, vessels))[0]
                target_coords = dwarf.x, dwarf.y
                print(f"The goblin vessel at {(self.x, self.y)} fires an arbalest!")
                hit = self.fire(wtype=weapon.ARBALEST, targeting=target_coords)
                print(hit)



    def fire(self, wtype, targeting):
        wcount = len(list(filter(lambda w: w == wtype, self.weapons)))
        #print(f"wtype {wtype} and wcount {wcount}")
        hit, damage, fatal = None, 0, False
        if wtype == weapon.MAGMA and wcount > 0:
            hit = player.parent_galaxy.cast(player.sector, (player.x, player.y), targeting)
            if isinstance(hit, Ship):
                damage, fatal = hit.hull, True
        elif wtype in [weapon.RAILGUN, weapon.ARBALEST] and wcount > 0:
            hit = player.parent_galaxy.get_tile(player.sector, *targeting)
            if isinstance(hit, Ship):
                for gun in range(min(wcount, self.ammo)):
                    damage += random.randint(5, 20)
                    self.ammo -= 1
                if (hit.hull - damage) <= 0:
                    fatal = True
                hit.hull -= damage
        if fatal:
            #print(f"hit reported to main routine as hit.x, hit.y = {[hit.x, hit.y]}")
            player.parent_galaxy.set_tile(player.sector, hit.x, hit.y, None, replace=True)
            #print(player.parent_galaxy.starmap[player.sector])
            #raise Exception("we're done here, watch the traceback")
        return hit, damage, fatal



class Star():
    def get_char(self): return "*"


class Station():
    def get_char(self): return "#"


def display_srs(s_designation, galaxy):
    print(f"short-range scan of sector {s_designation}...")
    s = galaxy.starmap[s_designation]
    print(s_designation.upper() + "  " + "".join([str(i) + " " * (3 - len(str(i))) for i in range(10)]))
    print(" " + "-" * 3 * 10)
    for rowi in range(len(s)):
        print(str(rowi) + "|", end="")
        for colj in range(len(s[rowi])):
            tile = s[rowi][colj]
            if tile:
                print(f" {tile.get_char()} ", end="")
            else:
                print(" . ", end="")
        print()
    #for row in s:
    #    for tile in row:
    #        try: print((tile.name, (tile.x, tile.y)))
    #        except: pass


def display_hud(player):
    print(f"{TIME_LIMIT - player.parent_galaxy.stardate} STARDATES REMAINING")
    print("SECTOR", player.sector.upper())
    print(f"HULL {player.hull} / ENERGY {player.energy} / SHIELDS {player.shields} / AMMO {player.ammo}")
    count = player.parent_galaxy.count_objects(player.sector)
    # print(f"""There are {count[0]} stars in this sector.
# There are {count[1]} stations in this sector.
# There are {0 if count[2] == 1 else (count[2] - 1)} enemy ships in this sector.""")

def display_lrs(s_designation, galaxy):

    sector_x, sector_y = galaxy.sector_coords_from_designation(s_designation)
    print(f"long-range scan from sector {s_designation}, {sector_x, sector_y}...")
    for y in range(4):
        for x in range(6):
            scanned_sector = galaxy.designation_from_sector_coords(x, y)
            if (abs(x - sector_x) <= 1) and (abs(y - sector_y) == 0) or (abs(x - sector_x) == 0) and (
                    abs(y - sector_y) <= 1): #if scanned sector is orthogonal from scanning sector
                scanned_sector = galaxy.designation_from_sector_coords(x, y)
                count = galaxy.count_objects(scanned_sector)
                print(f"  {scanned_sector.upper()}{count[0] if count[0]<10 else '!'}{count[1] if count[1]<10 else '!'}{count[2] if count[2]<10 else '!'}", end="")
            else:
                print(f"  {scanned_sector.upper()}   ", end="")
        print()


def player_jump(galaxy, player):
    x, y = -1, -1

    while not x >= 0 and x <= 9:
        try:
            x = int(input("local x coordinate (0-9)? "))
        except TypeError:
            pass
    while not y >= 0 and y <= 9:
        try:
            y = int(input("local y coordinate (0-9)? "))
        except TypeError:
            pass
    jump_dist = dist([player.x, player.y], [x, y])
    date_cost = int(jump_dist / 8) + 1
    energy_cost = int(jump_dist * 10)
    new_pos = (x, y)
    if galaxy.get_tile(player.sector, *new_pos):
        print("Scanners found an object at jump location, canceling.")
        return False
    if input(
            f"This will cost {energy_cost} energy and take {date_cost} stardates, confirm (y/n)? ").lower().strip() != "y":
        return False
    else:
        galaxy.tick(date_cost)
        player.move_to(player.sector, *new_pos)
        player.energy = max(player.energy - energy_cost, 0)
        return True


def player_warp(player):
    start_coords = player.parent_galaxy.sector_coords_from_designation(player.sector)
    destination = None
    while not (destination in player.parent_galaxy.starmap.keys() and destination != player.sector):
        destination = input("Destination sector? ")
    dest_coords = player.parent_galaxy.sector_coords_from_designation(destination)
    warp_dist = dist(start_coords, dest_coords)
    # print(f"[DEBUG-INFO] {start_coords} -> {dest_coords} = {warp_dist} distance")
    date_cost = int(warp_dist + 2)
    energy_cost = int(warp_dist) * 10 * 10
    if input(
            f"Warping to sector {destination} will use {energy_cost} energy and take {date_cost} stardates to prepare, confirm (y/n)?").lower().strip() != 'y':
        return False

    player.parent_galaxy.tick(date_cost)  # enemies take turns while prepping for warp
    # select a random empty tile in the destination sectors
    warp_point = (random.randint(0, 9), random.randint(0, 9))
    while player.parent_galaxy.get_tile(destination, *warp_point) != None:
        warp_point = (random.randint(0, 9), random.randint(0, 9))
    # and move there.
    player.energy = max(player.energy - energy_cost, 0)
    player.move_to(destination, *warp_point)
    return True  # confirm successful warp


def raise_shields(player):
    if player.energy == 0:
        print("No energy to divert to shields!")
    print(f"Shields are at {player.shields} energy")
    old_shields = player.shields
    divert = -1
    while divert < 0 or divert > player.energy:
        try:
            divert = int(input(f"Divert how much energy to shields? (0-{player.energy})"))
        except:
            pass
    player.energy -= divert
    player.shields += divert
    print(f"Raised shields to {player.shields} energy.")

def fire_weapons(player):
    w = int(input("0 - railguns, 1 - magma cannon: "))
    if w == weapon.RAILGUN:
        target = (-1, -1)
        while not player.parent_galaxy.valid_coords(player.sector, *target):
            try: target = int(input("target x: ")), int(input("target y:"))
            except: pass
        hit, damage, fatal = player.fire(w, target)
    elif w == weapon.MAGMA:
        dir = -1
        print(NAVGRID)
        while not (1 <= dir <= 8):
            dir = int(input("firing direction:"))
        hit, damage, fatal = player.fire(w, NAV_DIRECTIONS[dir])
    if not w in player.weapons:
        print("no such weapon. targeting cancelled.")
        return

    if isinstance(hit, Star):
        print(f"The {weapon.NAMES[w]} fire burns away in the star's corona.")
    elif isinstance(hit, Station):
        print(f"The {weapon.NAMES[w]} fire is deflected by the station's shields.")
    elif isinstance(hit, Ship):
        print(f"{weapon.NAMES[w].title()} fire strikes the {entity.NAMES[hit.parent_entity]} vessel at {hit.x}, {hit.y} for {damage} damage!")
        if fatal: print(f"*** The {entity.NAMES[hit.parent_entity]} vessel has been struck down. ***")
    if hit == None:
        print(f"The {weapon.NAMES[w]} fire dissipates into the void.")
    player.parent_galaxy.tick(1)



running = True

print("""*** Welcome to STAR DORF ***""")
player_name = input("What is your vessel named? ")

COMMAND_TEXT = f"""
* MISSION *
Destroy every goblin vessel in {TIME_LIMIT} turns.

* COMMANDS *
The {player_name} nav computer accepts:
    SRS: scan local sector
    LRS: scan long range
    JUMP: move in local sector
    WARP: warp between sectors
    FIRE: fire weapons
    SHIELD: raise shields
"""

INTRO_TEXT = f"""* MISSION *
The goblin empire has been skirmishing in sectors near Dwarven space. 
If their scouts are not defeated, they will spell doom for our glorious Dwarven civilization.
You've been put in command of the pride of the Dwarven navy, the warship {player_name}, outfitted with adamantine railguns and a magma cannon.
In these unconquered sectors, human starbases scattered about will be your only source of fuel and repair.
Your mission: strike down these goblin starships in {TIME_LIMIT} turns before they can overrun the Mountainhome.

For the glory of all {CIV_NAME}!"""

if input("Print intro/help now (y/n)? ").lower().strip() == "y":
    print(INTRO_TEXT)
input("[Enter] to embark on this mission...")

g = Galaxy()
player = Ship(player_name, entity.DWARF, 'a', [0, 0], [weapon.MAGMA, weapon.RAILGUN, weapon.RAILGUN, weapon.RAILGUN, weapon.RAILGUN], Ship.MAX_ENERGY, Ship.MAX_AMMO, g)
g.set_player(player)
g.gen_starmap(8, 8, 8)
g.set_tile('a', 0, 0, player)
#g.set_tile('a', 1, 1, Star())
#g.set_tile('a', 2, 2, Station())
# g.set_tile('a', 3, 3, Ship(name="Stenchfail", parent_entity=entity.GOBLIN, sector='a', weapons=[], coords=[0, 0], energy=100, parent_galaxy=g))
# display_srs('a', g)
# display_lrs('a', g)
#print(f"weapons: {player.weapons}")
while True:
    display_hud(player)
    # print(g.neighbors(player.sector, player.x, player.y, orthogonal=True))
    cmd = input("Enter command or 'help': ").lower().strip()
    if cmd == "jump":
        player_jump(g, player)
        input("...")
    elif cmd == "srs":
        display_srs(player.sector, g)
        input("...")
    elif cmd == "lrs":
        display_lrs(player.sector, g)
        input("...")
    elif cmd == "shields" or cmd == "shield":
        raise_shields(player)
    elif cmd == "warp":
        player_warp(player)
        input("...")
    elif cmd == "fire":
        fire_weapons(player)
        input("...")
    elif cmd == "help":
        print(COMMAND_TEXT)
        input("[enter]...")

    if list(filter(lambda n: isinstance(n, Station), g.neighbors(player.sector, player.x, player.y, orthogonal=True))):
        # print(g.neighbors(player.sector, player.x, player.y, orthogonal=True))
        # refuel, restock, repair
        print(f"\nShields lowered for docking...")
        player.shields = 0
        if player.energy < player.MAX_ENERGY:
            player.energy = player.MAX_ENERGY
            print(" Energy recharged.")
        if player.ammo < player.MAX_AMMO:
            player.ammo = player.MAX_AMMO
            print(" Ammunition restocked.")
        if player.hull < player.MAX_HULL:
            player.hull = player.MAX_HULL
            print(" Hull repaired.")
        player.shields = 500
        print(f" Shields raised to {player.shields}.")
