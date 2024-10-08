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

TIME_LIMIT = 35

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

class subsystem:
    IMP_ENGINE, WARP_ENGINE, TARGETING, SHIELD, SRS, LRS, NAV_COMPUTER = \
        range(7)
    NAMES = ("engines", "warp drive", "targeting", "shield emitters", "SR scanner",
             "LR scanner", "nav computer")

SUBSYSTEM_DAMAGE_THRESHOLD_PERCENTAGE = 0.35

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
        self.goblin_count = 0


    def gen_starmap(self, num_stars, num_goblins, num_stations):
        # print("populating parent_galaxy...")
        self.goblin_count = num_goblins
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
                if s[local_coords[0]][local_coords[1]] != None and self.count_objects(s_designation)[0] < 3:
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
                if s[local_coords[0]][local_coords[1]] != None and self.count_objects(s_designation)[1] == 0:
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
                    s[local_coords[0]][local_coords[1]] = Ship("Goblin Scout " + str(i), parent_entity=entity.GOBLIN,
                                                               sector=s_designation, weapons=[weapon.ARBALEST, weapon.ARBALEST],
                                                               coords=[local_coords[1],local_coords[0]], energy=random.randint(1,2), ammo=100,
                                                               systems=[subsystem.TARGETING, subsystem.IMP_ENGINE],
                                                               parent_galaxy=self)
                    placed = True

    def set_tile(self, sector, x, y, object, replace=False):
        # returns True on success
        if not replace and self.starmap[sector][y][x] != None:  # row-column!
            return False
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
        return objects

    def sector_from_designation(self, s_designation):
        return self.starmap[s_designation]

    def designation_from_sector_coords(self, x, y):
        numeric = x % self.STARMAP_WIDTH + y * self.STARMAP_WIDTH
        return list(self.starmap.keys())[numeric]

    def sector_coords_from_designation(self, s_designation):
        key = list('abcdefghijklmnopqrstuvwx').index(s_designation)
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
        if (TIME_LIMIT - self.stardate) <= 10 and random.random() < 0.2:
            try:
                sectors_under_attack = list(filter(lambda s: self.count_objects(s)[2] > 0 and self.count_objects(s)[1] > 0,
                                              list(self.starmap.keys())))
                alert_sector = random.choice(sectors_under_attack)
                print("\n" + f"A station in sector {alert_sector.upper()} reports signs of goblin activity.")
            except:
                pass


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

    def __init__(self, name, parent_entity, sector, coords, weapons, energy, ammo, systems: [int], parent_galaxy: Galaxy):
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
        self.known_space = []
        self.subsystems = {}
        for sys in systems:
            self.subsystems[sys] = 1

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

    def move_to(self, new_sector, new_x, new_y, clamp = True, check = False):
        if clamp:
            new_x = max(0, new_x)
            new_x = min(new_x, self.parent_galaxy.SECTOR_WIDTH - 1)
            new_y = max(0, new_y)
            new_y = min(new_y, self.parent_galaxy.SECTOR_HEIGHT - 1)
        #print(f" {self.name} moving to {(new_x, new_y)}")
        if check and self.parent_galaxy.get_tile(new_sector, new_x, new_y) != None:
            return False, [new_x, new_y]
        self.parent_galaxy.set_tile(self.sector, self.x, self.y, None, True)  # clear current tile

        self.sector = new_sector
        self.x = new_x
        self.y = new_y

        self.parent_galaxy.set_tile(self.sector, self.x, self.y, self, False)  # add to destination tile

        self.learn_sector(self.sector)

        return True, [self.x, self.y]

    def tick(self):
        self.shields *= 0.97
        if self.parent_entity == entity.GOBLIN:
            if random.random() < 2/3:
                try:
                    if self.get_capability(subsystem.IMP_ENGINE) < 1:
                        print("The goblin vessel's engines sputter uselessly!")
                        return
                    dx, dy = [random.randint(-3, 3), random.randint(-3, 3)]
                    newx, newy = self.x + dx, self.y + dy
                    while isinstance(self.parent_galaxy.get_tile(self.sector, newx, newy), Ship):
                        dx, dy = [random.randint(-3, 3), random.randint(-3, 3)]
                        newx, newy = self.x + dx, self.y + dy
                    result = self.move_to(self.sector, newx, newy)
                    print(f"Goblin vessel moves to {(result[1], result[2])}.")
                    if not result[0]:
                        print("Unfortunately, there was a station there already.\nKABOOM!")
                        self.parent_galaxy.clear_tile(self.sector, result[1], result[2])
                        self.die()

                except Exception as e:
                    pass
            else:
                if self.get_capability(subsystem.TARGETING) < 1:
                    print("The goblin vessel's weapons misfire!")
                    return
                vessels = self.parent_galaxy.get_objects(self.sector)[2]
                dwarf = self.parent_galaxy.player
                target_coords = dwarf.x, dwarf.y
                hit, damage, fatal = self.fire(wtype=weapon.ARBALEST, targeting=target_coords)
                print(f"The goblin vessel at {(self.x, self.y)} fires an arbalest!")
                print(f"The Plasma Arbalest bolts strike for {damage} damage!")
                if random.random() < 0.15:
                    print("The goblin vessel summons a burst of speed!")
                    self.tick()



    def get_capability(self, subsystem_type):
        if subsystem_type in self.subsystems:
            return self.subsystems[subsystem_type]
        else: return 0

    def get_shield_absorption(self):
        if self.get_capability(subsystem.SHIELD) >= 0.9:
            return 0.9
        else:
            return (self.get_capability(subsystem.SHIELD) + 0.9)/2

    def fire(self, wtype, targeting):
        wcount = len(list(filter(lambda w: w == wtype, self.weapons)))
        hit, damage, fatal = None, 0, False
        if wtype == weapon.MAGMA and wcount > 0:
            self.energy -= 100
            hit = self.parent_galaxy.cast(self.sector, (self.x, self.y), targeting)
            if isinstance(hit, Ship):
                damage, fatal = hit.hull, True
        elif wtype in [weapon.RAILGUN, weapon.ARBALEST] and wcount > 0:
            hit = self.parent_galaxy.get_tile(self.sector, *targeting)
            if isinstance(hit, Ship):
                for gun in range(min(wcount, self.ammo)):
                    damage += random.randint(1, 20)
                    self.ammo -= 1
                if damage >= hit.hull * SUBSYSTEM_DAMAGE_THRESHOLD_PERCENTAGE or random.random()<0.2:
                    # target a subsystem
                    sub = random.choice(list(hit.subsystems.keys()))
                    if sub in [subsystem.IMP_ENGINE, subsystem.WARP_ENGINE]:
                        # chance to re-roll if engine hit
                        # because I'm nice :)
                        if random.random() <= 0.5:
                            sub = random.choice(list(hit.subsystems.keys()))
                    if sub == subsystem.NAV_COMPUTER:
                        if hit is hit.parent_galaxy.player:
                            hit.forget_sector(random.choice(hit.known_space))
                            hit.forget_sector(random.choice(hit.known_space))
                    hit.subsystems[sub] = max(0, hit.subsystems[sub] - random.random()/5)
                    print('\nALERT: ' if hit is hit.parent_galaxy.player else '', end = '')
                    print(f"{hit.name} {subsystem.NAMES[sub]} damaged!")

                absorbed_damage = min(hit.shields, int(damage * hit.get_shield_absorption()))
                hit.shields -= absorbed_damage
                hit.hull -= (damage - absorbed_damage)
                if hit.hull <= 0:
                    fatal = True
        if fatal:
            hit.die()
        return hit, damage, fatal

    def die(self):
        self.parent_galaxy.set_tile(self.sector, self.x, self.y, None, replace=True)
        if self.parent_entity == entity.GOBLIN:
            self.parent_galaxy.goblin_count -= 1

    def learn_sector(self, designation: str):
        if not designation in self.known_space:
            self.known_space.append(designation)

    def forget_sector(self, designation: str):
        try:
            self.known_space.remove(designation)
        except:
            pass


class Star():
    def get_char(self): return "*"


class Station():
    def get_char(self): return "#"
