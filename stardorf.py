import random

from stardorf_classes import *

def display_srs(s_designation, galaxy: Galaxy):
    print(f"short-range scan of sector {s_designation}...")
    if galaxy.player.get_capability(subsystem.LRS) < 0.25:
        print("Local scanner inoperable. Scan canceled.")
        return
    s = galaxy.starmap[s_designation]
    print(s_designation.upper() + "  " + "".join([str(i) + " " * (3 - len(str(i))) for i in range(10)]))
    print(" " + "-" * 3 * 10)
    malfunction = False # placeholder
    for rowi in range(len(s)):
        print(str(rowi) + "|", end="")
        for colj in range(len(s[rowi])):
            tile = s[rowi][colj]
            if not malfunction:
                if tile:
                    print(f" {tile.get_char()} ", end="")
                else:
                    print(" . ", end="")
            else:
                print("   ", end="")
        print()


def display_hud(player):
    print(f"{TIME_LIMIT - player.parent_galaxy.stardate} STARDATES{(',', '!')[(TIME_LIMIT-player.parent_galaxy.stardate) <= TIME_LIMIT/2]} {player.parent_galaxy.goblin_count} GOBLINS")
    print("SECTOR", player.sector.upper())
    print(f"HULL {player.hull} / ENERGY {player.energy} / SHIELDS {player.shields:.2f} / AMMO {player.ammo}")
    count = player.parent_galaxy.count_objects(player.sector)

def display_lrs(s_designation, galaxy, player: Ship):
    sector_x, sector_y = galaxy.sector_coords_from_designation(s_designation)
    print(f"long-range scan from sector {s_designation}, {sector_x, sector_y}...")
    if player.get_capability(subsystem.LRS) < 0.25:
        print("LR scanner inoperable. Scan canceled.")
        return
    malfunction = False # placeholder
    for y in range(4):
        for x in range(6):
            scanned_sector = galaxy.designation_from_sector_coords(x, y)
            if not malfunction or (malfunction and not ((hash(s_designation) % 10 == y) and (hash(s_designation.upper()) % 10 == x))):
                if (abs(x - sector_x) <= 1) and (abs(y - sector_y) == 0) or (abs(x - sector_x) == 0) and (
                        abs(y - sector_y) <= 1): #if scanned sector is orthogonal from scanning sector...
                    player.learn_sector(scanned_sector) # add it to known space
                if scanned_sector in player.known_space: # and display a known sector
                    scanned_sector = galaxy.designation_from_sector_coords(x, y)
                    count = galaxy.count_objects(scanned_sector)
                    print(f"  {scanned_sector.upper()}{count[0] if count[0] < 10 else '!'}{count[1] if count[1] < 10 else '!'}{count[2] if count[2] < 10 else '!'}",
                        end="")
                else:
                    print(f"  {scanned_sector.upper()}   ", end="")
            else: print(f"  {scanned_sector.upper()}   ", end="")
        print()


def player_jump(galaxy, player):
    if player.get_capability(subsystem.IMP_ENGINE) == 0:
        print("Your impulse engines are too damaged to move.")
        return False

    x, y = -1, -1

    while not x >= 0 and x <= 9:
        try:
            x = int(input("local x coordinate (0-9)? "))
        except:
            return
    while not y >= 0 and y <= 9:
        try:
            y = int(input("local y coordinate (0-9)? "))
        except:
            return
    jump_dist = dist([player.x, player.y], [x, y])
    date_cost = int((jump_dist + jump_dist*(1 - player.get_capability(subsystem.IMP_ENGINE))) / 8) + 1
    energy_cost = int((jump_dist + jump_dist*(1 - player.get_capability(subsystem.IMP_ENGINE))) * 10)
    new_pos = (x, y)
    if galaxy.get_tile(player.sector, *new_pos):
        print("Scanners found an object at jump location, canceling.")
        return False
    if input(
            f"Jump will cost {energy_cost} energy and take {date_cost} stardates, confirm (y/n)? ").lower().strip() != "y":
        return False
    else:
        galaxy.tick(date_cost)
        player.move_to(player.sector, *new_pos)
        player.energy = max(player.energy - energy_cost, 0)
        return True


def player_warp(player):
    if player.get_capability(subsystem.WARP_ENGINE) == 0:
        print("Your warp drive is too damaged.")
        return False
    start_coords = player.parent_galaxy.sector_coords_from_designation(player.sector)
    destination = ""
    while not destination.lower() in player.parent_galaxy.starmap.keys():
        destination = input("Destination sector? ").lower()
        if destination == player.sector:
            return
    dest_coords = player.parent_galaxy.sector_coords_from_designation(destination)
    warp_dist = dist(start_coords, dest_coords)
    # print(f"[DEBUG-INFO] {start_coords} -> {dest_coords} = {warp_dist} distance")
    date_cost = int(warp_dist + warp_dist*(1 - player.get_capability(subsystem.WARP_ENGINE)))
    energy_cost = int(warp_dist + warp_dist*(1 - player.get_capability(subsystem.WARP_ENGINE))) * 10 * 5
    if input(
            f"Warping to sector {destination} will use {energy_cost} energy and take {date_cost} stardates to prepare, confirm (y/n)? ").lower().strip() != 'y':
        return False

    player.parent_galaxy.tick(date_cost)  # enemies take turns while prepping for warp
    if player.get_capability(subsystem.WARP_ENGINE) < 0.15 and random.random() < 0.5:
        accident_sector = random.choice(list(player.parent_galaxy.starmap.keys())).upper()
        print(f"A freak glitch in the damaged warp drive sends you to sector {accident_sector} instead!")
    # select a random empty tile in the destination sectors
    warp_point = (random.randint(0, 9), random.randint(0, 9))
    while player.parent_galaxy.get_tile(destination, *warp_point) is not None:
        warp_point = (random.randint(0, 9), random.randint(0, 9))
    # and move there.
    player.energy = max(player.energy - energy_cost, 0)
    player.move_to(destination, *warp_point)
    return True  # confirm successful warp


def raise_shields(player):
    if player.energy == 0:
        print("No energy to divert!")
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
    try:
        w = int(input("0 - railguns, 1 - magma cannon: "))
    except:
        return
    misfire_chance = 1 - player.get_capability(subsystem.TARGETING)
    #if misfire_chance < 0.25: misfire_chance = 0.0
    if w in player.weapons:
        if not random.random() < misfire_chance:
            if w == weapon.RAILGUN:
                target = (-1, -1)
                while not player.parent_galaxy.valid_coords(player.sector, *target):
                    try: target = int(input("target x: ")), int(input("target y: "))
                    except: pass
                hit, damage, fatal = player.fire(w, target)
            elif w == weapon.MAGMA:
                dir = -1
                print(NAVGRID)
                while not (1 <= dir <= 8):
                    try:
                        dir = int(input("firing direction:"))
                    except:
                        return
                hit, damage, fatal = player.fire(w, NAV_DIRECTIONS[dir])
        else:
            print("Your damaged targeting system misfires!")
            return
    else:
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

def examine_subsystems(player):
    print("SUBSYSTEM NAME - HEALTH - STATUS")
    for sub in player.subsystems:
        health = player.subsystems[sub]
        status = "almost junk" if health < 0.25 else ("damaged" if health < 0.75 else "functional")
        status = "disabled" if health == 0 else status
        print(f"{subsystem.NAMES[sub].upper():<17}{str(round(health*100, 1))+"%":<9}{status}")

print("""*** Welcome to STAR DORF ***""")
player_name = input("What is your vessel named? ")

COMMAND_TEXT = f"""
* MISSION *
Victory: Destroy every goblin vessel in {TIME_LIMIT} turns.
Failure: Reach 0 hull integrity, 0 energy, or the time limit.

* COMMANDS *
The {player_name} nav computer accepts:
    SRS: scan local sector
        @ = you, * = star, # = station, g = goblin
    LRS: scan long range
        star count, station count, enemy count
    JUMP: move in local sector
    WARP: warp between sectors
    FIRE: fire weapons
        Railgun can fire at any spot, but takes ammo. Chance of disabling enemy subsystems.
        Magma cannon destroys any spaceship, but can only fire orthogonally. Costs 100 energy.
    SHIELD: transfer energy to shields. Shields will decay over time.
    SYS: view subsystem status

Moving orthogonally adjacent to a station will repair, refuel and restock your vessel.
It will also slowly repair subsystems.
"""

INTRO_TEXT = f"""* MISSION *
The goblin empire has been skirmishing in sectors near Dwarven space. 
If their scouts are not defeated, they will spell doom for our glorious Dwarven civilization.
You command the {player_name}, pride of the Dwarven navy, outfitted with adamantine railguns and a magma cannon.
In these unconquered sectors, human starbases scattered about will be your only source of fuel and repair.
Your mission: strike down these goblin starships in {TIME_LIMIT} turns before they can overrun the Mountainhome.

For the glory of all {CIV_NAME}!"""


if input("Print intro (y/n)? ").lower().strip() == "y":
    print(INTRO_TEXT)
if input("Print help (y/n)? ").lower().strip() == "y":
    print(COMMAND_TEXT)
input("[Enter] to embark on this mission...")

g = Galaxy()
g.gen_starmap(12, 8, 5)
start_sector = random.choice(list(g.starmap.keys()))
player_global = Ship(player_name, entity.DWARF, start_sector, [0, 0],
                     [weapon.MAGMA, weapon.RAILGUN, weapon.RAILGUN, weapon.RAILGUN, weapon.RAILGUN],
                     Ship.MAX_ENERGY,
                     Ship.MAX_AMMO,
                     [subsystem.IMP_ENGINE, subsystem.WARP_ENGINE, subsystem.NAV_COMPUTER, subsystem.LRS,
                      subsystem.SRS, subsystem.SHIELD, subsystem.TARGETING],
                     g)
g.set_player(player_global)
g.set_tile(start_sector, 0, 0, player_global)

win = False
while True:
    display_hud(player_global)
    cmd = input("Enter command or 'help': ").lower().strip()
    if cmd == "jump":
        player_jump(g, player_global)
    elif cmd == "srs":
        display_srs(player_global.sector, g)
    elif cmd == "lrs":
        display_lrs(player_global.sector, g, player_global)
    elif cmd == "shields" or cmd == "shield":
        raise_shields(player_global)
    elif cmd == "warp":
        player_warp(player_global)
    elif cmd == "fire":
        fire_weapons(player_global)
    elif cmd == "sys":
        examine_subsystems(player_global)
    elif cmd == "help":
        print(COMMAND_TEXT)
        input("[enter]...")
    else:
        print(f"The {player_name} doesn't understand '{cmd}'.")
    #refuel, restock, repair at stations
    if list(filter(lambda n: isinstance(n, Station), g.neighbors(player_global.sector, player_global.x, player_global.y, orthogonal=True))):
        # print(g.neighbors(player_global.sector, player_global.x, player_global.y, orthogonal=True))
        print(f"\nShields lowered for docking...")
        player_global.shields = 0
        if player_global.energy < player_global.MAX_ENERGY:
            player_global.energy = player_global.MAX_ENERGY
            print(" Energy recharged.")
        if player_global.ammo < player_global.MAX_AMMO:
            player_global.ammo = player_global.MAX_AMMO
            print(" Ammunition restocked.")
        if player_global.hull < player_global.MAX_HULL:
            player_global.hull = player_global.MAX_HULL
            print(" Hull repaired.")
        repaired_subst = []
        for subst in player_global.subsystems:
            if player_global.subsystems[subst] < 1.0:
                player_global.subsystems[subst] = max(player_global.subsystems[subst] * 1.2, 1.0)
                print(f"{subsystem.NAMES[subst]}: repaired to {player_global.subsystems[subst]:.1f}% capability.")

        player_global.shields = 100
        print(f"Shields raised to {player_global.shields}.")
    # check for win or loss state
    if player_global.parent_galaxy.goblin_count <= 0:
        win = True
        break
    if player_global.hull <= 0 or player_global.energy <= 0:
        win = False
        break
    if (TIME_LIMIT - player_global.parent_galaxy.stardate) <= 0:
        win = False
        break

#handle win or loss
if win:
    print(f"The {player_name} has driven out the goblin scouts, keeping their vessels from siegeing the "
          f"Mountainhome.\nYour name has been engraved in the depths of the ancestral asteroids.")
    input("...")
else:
    if player_global.hull <= 0 and player_global.parent_galaxy.goblin_count > 1:
        print(f"The {player_name} has fallen in battle against the goblin scouts.")
    elif player_global.hull <= 0 and player_global.parent_galaxy.goblin_count == 1:
        print(f"The {player_name} has fallen in battle against the last goblin scout.")
    elif player_global.energy <= 0:
        print(f"The {player_name} is stranded in space, systems falling cold as her energy bleeds away.")
    elif (TIME_LIMIT - player_global.parent_galaxy.stardate) <= 0:
        print(f"The {player_name} fought tirelessly, but she could not slow down the scouts quite fast enough.")
    print("Boldened by their victory against a Dwarven warship, the goblins move ever closer to the Mountainhome...")
    input("...")
