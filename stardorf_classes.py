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
                    #print(f"added {tile}, {entity.NAMES[tile.parent_entity]} in {tile.sector}")
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
        self.known_space = []

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

        self.learn_sector(self.sector)

    def tick(self):
        #DONE: AI vessels should actually move on grid. fix bug and implement energy
        #print(f"vessel {self.name} tick called")
        if self.parent_entity == entity.GOBLIN:
            self.energy = [2, 0, 1][self.energy]  # cycle thru energy
            if self.energy == 2:
                try:
                    dx, dy = [random.randint(-3, 3), random.randint(-3, 3)]
                    newx, newy = self.x + dx, self.y + dy
                    self.move_to(self.sector, newx, newy)
                    print(f"Goblin vessel moves to {(self.x, self.y)}.")
                except Exception as e:
                    print(" "+str(e))
            elif self.energy == 1:
                vessels = self.parent_galaxy.get_objects(self.sector)[2]
                #print(f"goblin sees: {list(v.parent_entity for v in vessels)}")
                dwarf = list(filter(lambda v: v.parent_entity == entity.DWARF, vessels))[0]
                target_coords = dwarf.x, dwarf.y
                hit, damage, fatal = self.fire(wtype=weapon.ARBALEST, targeting=target_coords)
                print(f"The goblin vessel at {(self.x, self.y)} fires an arbalest!")
                print(f"The Plasma Arbalest bolts strike for {damage} damage!")
                #print(hit)



    def fire(self, wtype, targeting):
        wcount = len(list(filter(lambda w: w == wtype, self.weapons)))
        #print(f"wtype {wtype} and wcount {wcount}")
        hit, damage, fatal = None, 0, False
        if wtype == weapon.MAGMA and wcount > 0:
            hit = self.parent_galaxy.cast(self.sector, (self.x, self.y), targeting)
            if isinstance(hit, Ship):
                damage, fatal = hit.hull, True
        elif wtype in [weapon.RAILGUN, weapon.ARBALEST] and wcount > 0:
            hit = self.parent_galaxy.get_tile(self.sector, *targeting)
            if isinstance(hit, Ship):
                for gun in range(min(wcount, self.ammo)):
                    damage += random.randint(5, 20)
                    self.ammo -= 1
                absorbed_damage = min(hit.shields, damage)
                hit.shields -= absorbed_damage
                hit.hull -= (damage - absorbed_damage)
                if hit.hull <= 0:
                    fatal = True
        if fatal:
            #print(f"hit reported to main routine as hit.x, hit.y = {[hit.x, hit.y]}")
            self.parent_galaxy.set_tile(self.sector, hit.x, hit.y, None, replace=True)
            if hit.parent_entity == entity.GOBLIN:
                self.parent_galaxy.goblin_count -= 1
            #print(player_global.parent_galaxy.starmap[player_global.sector])
            #raise Exception("we're done here, watch the traceback")
        return hit, damage, fatal

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
