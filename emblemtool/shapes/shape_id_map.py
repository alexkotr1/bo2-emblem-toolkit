"""
BO2 shape name lists (from the emblem editor's known category data) plus
the numeric ID -> name mapping we're calibrating via the `probe` command.

known_ids: fill in as you calibrate. {id: "Category/Name"}
"""

emblemdata = {
    "type": ['Letter A', 'Letter B', 'Letter C', 'Letter D', 'Letter E', 'Letter F', 'Letter G', 'Letter H', 'Letter I', 'Letter J', 'Letter K', 'Letter L', 'Letter M', 'Letter N', 'Letter O', 'Letter P', 'Letter Q', 'Letter R', 'Letter S', 'Letter T', 'Letter U', 'Letter V', 'Letter W', 'Letter X', 'Letter Y', 'Letter Z', 'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'],
    "tools": ['Half Circle', 'Quarter Circle', 'Half Heart', 'Cone', 'Thimble', 'Kiss', 'Scribble', 'Round Square', 'Ninja Star', 'Half Star', 'Shuriken', 'Half Shuriken', 'Lamp Shade', 'Pyramid', 'Half Tube', 'Tube', 'Golf Flag', 'Tongue', 'Broken Column', 'Visor', 'Bone', 'Armchair', 'Oven Mitt', 'Wind Sock', 'Podium', 'Pie Slice', 'Flashlight', 'Scoop', 'Flag Breeze', 'Flag No Wind', 'Axe', 'Fedora', 'Rock', 'Bike Ramp', 'Rock Shadow', 'Half Column', 'Monolith', 'Top Hat', 'Igloo', 'Mane', 'Swoop', 'Shield', 'Paint Splash', 'Pillow', 'Asterisk Full', 'Biohazard', 'Curved Line', 'Smile Outline', 'Heart', 'Ice Star', 'Triangle Wide', 'Tent', 'Half Short Hair', 'Half Mustache', 'Half Long Hair', 'Full Circle', 'Circle 02', 'Diamond', 'Rectangle Medium', 'Square Full', 'Treyarch'],
    "ranks": ['Private 1st Class', 'Lance Corporal', 'Corporal', 'Sergeant', 'Staff Sergeant', 'Gunnery Sergeant', 'Master Sergeant', 'Master Gunnery Sergeant', 'Second Lieutenant', 'Lieutenant', 'Captain', 'Major', 'Lt. Colonel', 'Colonel', 'Brigadier General', 'Major General', 'Lt. General', 'General', 'Commander'],
    "gear": ['KAP-40 Qualified', 'Tac-45 Qualified', 'B23R Qualified', 'Executioner Qualified', 'Five-seven Qualified', 'MP7 Qualified', 'Skorpion EVO Qualified', 'PDW-57 Qualified', 'Chicom CQB Qualified', 'MSMC Qualified', 'Vector K10 Qualified', 'M8A1 Qualified', 'SCAR-H Qualified', 'AN-94 Qualified', 'SWAT-556 Qualified', 'Type 25 Qualified', 'FAL OSW Qualified', 'SMR Qualified', 'M27 Qualified', 'MTAR Qualified', 'Mk 48 Qualified', 'QBB LSW Qualified', 'LSAT Qualified', 'HAMR Qualified', 'Ballista Qualified', 'SVU-AS Qualified', 'DSR 50 Qualified', 'XPR-50 Qualified', 'R870 MCS Qualified', 'M1216 Qualified', 'S12 Qualified', 'KSG Qualified', 'SMAW Qualified', 'FHJ-18 AA Qualified', 'RPG Qualified', 'Assault Shield Qualified', 'Crossbow Qualified', 'Ballistic Knife Qualified', 'Peacekeeper Qualified'],
    "emblems": ['Elite Member', 'Elite Founder', 'Default Emblem', 'Crushing Victory', 'Crushing Victory ', 'Crushing Victory  ', 'Crushing Victory   ', 'Crushing Victory    ', 'Shutout', 'Shutout ', 'Crushing Victory     ', 'Annihilation Victory', 'Relentless', 'Triple Kill', 'Avenger', 'Savior', 'Unstoppable', 'Ninja', 'Last Man Standing', 'The Finisher', 'Shutout Round', 'Bomb Protector', 'Interruption', 'Bomb Protector ', 'Interruption ', 'Super Star', 'Double Denied', 'Bravo Hot', 'Alpha Lockdown', 'Bravo Lockdown', 'Charlie Lockdown', 'Synchronized Attack', 'Point Man', 'Zone Sweep', 'Trick Shot', 'Clean House', "Slice 'n Dice", 'Wet Work', 'Situation Critical', 'Far Sighted', 'Tick Tick Boom', 'Pistoleer', 'Say Hello', 'Headhunter', 'Sharpshooter', 'Close Quarters Expert', 'Counter Trapper', 'Surprise Package', 'Counter Hacker', 'Aircraft Hunter', 'Clean Sweep', 'Grab n Go', 'Protected Kill', 'Close Call', 'Arch Nemesis', 'Circus Act', 'Found Kills', 'Short Fuse', 'High Voltage', 'Follow Through', 'Stick Around', 'Hail Mary', 'Brutal Killer', 'Fury Killer', 'Frenzy Killer', 'Super Killer', 'All Clear', 'Assisted Homicide', 'Backdraft', 'Guerilla Warfare', 'Vandalism', 'Action Hero', 'Commando', 'Perk Greed', 'Danger Close', 'Overkill', 'Gunfighter', 'Killjoy', 'Pest Control', 'Drones Eliminated', 'Dog Pound', 'Down Dog', 'Opportunistic', 'Maximum Payload', 'Anti-Swatter', 'Threat Neutralized', 'Special Delivery', 'RC Multi Bomber', 'Heavy Cover', 'Thumper', 'Shredder', 'Focus Fire', 'Tracker', 'Guide Dogs', 'Hard Counter', 'Overcooked', 'Cancelled Out', 'Make It Rain', 'Got Your Back', 'Small Game Hunter', 'Big Game Hunter', 'Thief', 'Merciless', 'Ruthless', 'Hard to Kill', 'Invincible'],
}

# Calibrated: user placed tools[0..19] in sequential grid order and
# confirmed the resulting layer shapeIds (137..156) match that order.
# tools category confirmed to start at offset 137.
known_ids = {i: f"tools/{name}" for i, name in enumerate(emblemdata["tools"][:20], start=137)}

# Calibrated: user placed tools[20..51] (32 shapes, one full emblem slot) in
# sequential layer order and the captured shapeIds (157..188) matched exactly.
known_ids.update({i: f"tools/{name}" for i, name in enumerate(emblemdata["tools"][20:52], start=157)})

# Calibrated: user placed tools[52..60] (9 shapes) in sequential layer order
# and the captured shapeIds (189..197) matched exactly. tools category (61
# shapes, IDs 137..197) is now fully confirmed.
known_ids.update({i: f"tools/{name}" for i, name in enumerate(emblemdata["tools"][52:61], start=189)})

# Calibrated: user placed 2 emblems shapes and identified them directly by
# what appeared in-game: "Triple Kill" -> 48, "Default Emblem" -> 259. These
# are NOT contiguous (gap of 211, not the ~12 the user expected from list
# position), so the emblems category's IDs likely aren't assigned in a
# simple sequential block the way tools[] was - each shape needs its own
# direct placement-and-capture confirmation rather than inferring a range.
known_ids[48] = "emblems/Triple Kill"
known_ids[259] = "emblems/Default Emblem"

# Calibrated: live memory-read of BO2 PC's emblem editor (address 0x0294B7A0
# in t6mp.exe holds the emblem currently being edited) while scrolling
# steadily through the `type` category from Letter A. CORRECTED 2026-07-17:
# originally logged as 218..252 (assumed 253="Nine" by extrapolation), but a
# later direct write+screenshot check found id 218 is actually "Letter B"
# and id 252 is "Nine" - the whole category was off by one. True range is
# 217..252 (36 shapes, Letter A through Nine), confirmed directly.
known_ids.update({i: f"type/{name}" for i, name in enumerate(emblemdata["type"], start=217)})

# Calibrated: same live memory-read technique, scrolled steadily through the
# entire `ranks` category (19 shapes, Private 1st Class -> Commander).
# Logged IDs 198..216 in a perfect 1-per-step ascending sequence - ranks
# category is now fully confirmed.
known_ids.update({i: f"ranks/{name}" for i, name in enumerate(emblemdata["ranks"], start=198)})

# Calibrated: same live memory-read technique, scrolled steadily through
# `gear` (39 shapes) starting from KAP-40 Qualified. Logged IDs 0..37 in a
# perfect 1-per-step ascending sequence (id == list index for this
# category) - confirmed against gear[0..37].
known_ids.update({i: f"gear/{name}" for i, name in enumerate(emblemdata["gear"][:38], start=0)})
# gear[38] ("Peacekeeper Qualified") is a bonus DLC weapon added after the
# base 38-weapon roster, so it doesn't continue the 0..37 sequence - found
# via direct write+screenshot probing just past the highest id in use
# (259), confirmed by exact image match.
known_ids[260] = "gear/Peacekeeper Qualified"

# emblems category doesn't map cleanly by list order (unlike the categories
# above) - confirmed non-contiguously by reading each shape's in-game name
# directly (translating the Russian UI text) while live-reading the memory
# address. `emblems` spans two ID blocks: 38-136 and 253-259 (99+7=106,
# matching the category's full size).
# "Interruption" confirmed at id=96 (list has two identically-named entries,
# index 22 and 24 with a trailing space - assumed index22, unconfirmed which
# exact tier/image this is if they differ).
known_ids[96] = "emblems/Interruption"
# Confirmed directly via memory read while hovering: no reliable formula
# links list-index to id here (tested id=list_index+35 against Triple
# Kill(13->48, fits) and Interruption(22->57 predicted, but actually 96) -
# contradicts, so each emblems shape still needs individual confirmation.
known_ids[128] = "emblems/Guide Dogs"

# A memory string table (CHALLENGE_<KEY> entries, English, next to the
# localized display text) lists emblems in an internal order and looked
# like it might let us compute IDs by counting position from a confirmed
# anchor - tested against Guide Dogs(confirmed 128) and Thief: table
# position implied Thief should be 136+11=... (offset math predicted 255),
# but direct repeated memory reads (incl. after deliberately re-selecting
# it) confirmed Thief is actually 136. So ~3 of the ~11 table entries
# between them don't correspond to unique shape IDs (duplicates/non-emblem
# entries, unclear which) - the table's *position* can't be trusted to
# derive IDs, only its *names* are useful. Don't rely on offset-counting
# from this table again; confirm each id individually.
known_ids[136] = "emblems/Thief"
known_ids[116] = "emblems/Down Dog"

# Confirmed via direct write-to-memory + screenshot of the live editor's
# main preview box (github.com/olie304/CallOfDutyEmblemSpecs documents this
# is safe - BO2 doesn't mind memory reads/writes). The 5 "Crushing Victory"
# entries in emblemdata are a scraping artifact from the source project -
# they're 5 completely different images (single soldier, two soldiers,
# briefcase, ammo crate, three flags), not 5 tiers of one icon. Their
# *images* are confirmed correct for these IDs even though the display name
# is almost certainly wrong for 4 of the 5 - the name field here is really
# "which file to use", not a claim about the true achievement name.
known_ids[38] = "emblems/Crushing Victory"
known_ids[39] = "emblems/Crushing Victory "
known_ids[40] = "emblems/Crushing Victory  "
known_ids[41] = "emblems/Crushing Victory   "
known_ids[42] = "emblems/Crushing Victory    "
known_ids[43] = "emblems/Shutout"
known_ids[44] = "emblems/Shutout "
# reference_shapes has a 6th "Crushing Victory" image (5 trailing spaces)
# that isn't referenced by any emblemdata name at all - an orphaned asset
# from the same scraping bug. Used directly by filename since there's no
# corresponding list entry.
known_ids[45] = "emblems/Crushing Victory     "
known_ids[46] = "emblems/Annihilation Victory"
known_ids[47] = "emblems/Relentless"
known_ids[49] = "emblems/Avenger"
known_ids[50] = "emblems/Savior"
known_ids[51] = "emblems/Unstoppable"
known_ids[52] = "emblems/Ninja"
known_ids[53] = "emblems/Last Man Standing"
known_ids[54] = "emblems/The Finisher"
known_ids[55] = "emblems/Shutout Round"
known_ids[56] = "emblems/Bomb Protector"
# Same image as id96 (shield+skull) - legitimately reused for a different
# numeric id, not a labeling conflict.
known_ids[57] = "emblems/Interruption"
known_ids[58] = "emblems/Bomb Protector "
known_ids[59] = "emblems/Interruption "
known_ids[60] = "emblems/Super Star"
known_ids[61] = "emblems/Double Denied"
known_ids[62] = "emblems/Bravo Hot"
known_ids[63] = "emblems/Alpha Lockdown"
known_ids[64] = "emblems/Bravo Lockdown"
known_ids[65] = "emblems/Charlie Lockdown"
known_ids[66] = "emblems/Synchronized Attack"
known_ids[67] = "emblems/Point Man"
known_ids[68] = "emblems/Zone Sweep"
known_ids[69] = "emblems/Trick Shot"
known_ids[70] = "emblems/Clean House"
known_ids[71] = "emblems/Slice 'n Dice"
known_ids[72] = "emblems/Wet Work"
known_ids[73] = "emblems/Situation Critical"
known_ids[74] = "emblems/Far Sighted"
known_ids[75] = "emblems/Tick Tick Boom"
known_ids[76] = "emblems/Pistoleer"
known_ids[77] = "emblems/Say Hello"
known_ids[78] = "emblems/Headhunter"
known_ids[79] = "emblems/Sharpshooter"
known_ids[80] = "emblems/Close Quarters Expert"
known_ids[81] = "emblems/Counter Trapper"
known_ids[82] = "emblems/Surprise Package"
# Same bolt-cutters image as id48, legitimately reused.
known_ids[83] = "emblems/Counter Hacker"
known_ids[84] = "emblems/Aircraft Hunter"
known_ids[85] = "emblems/Clean Sweep"
known_ids[86] = "emblems/Grab n Go"
known_ids[87] = "emblems/Protected Kill"
known_ids[88] = "emblems/Close Call"
known_ids[89] = "emblems/Arch Nemesis"
known_ids[90] = "emblems/Circus Act"
known_ids[91] = "emblems/Found Kills"
known_ids[92] = "emblems/Short Fuse"
known_ids[93] = "emblems/High Voltage"
known_ids[94] = "emblems/Follow Through"
known_ids[95] = "emblems/Stick Around"
known_ids[97] = "emblems/Brutal Killer"
known_ids[98] = "emblems/Fury Killer"
known_ids[99] = "emblems/Frenzy Killer"
known_ids[100] = "emblems/Super Killer"
known_ids[101] = "emblems/All Clear"
known_ids[102] = "emblems/Assisted Homicide"
known_ids[103] = "emblems/Backdraft"
known_ids[104] = "emblems/Guerilla Warfare"
known_ids[105] = "emblems/Vandalism"
known_ids[106] = "emblems/Action Hero"
known_ids[107] = "emblems/Commando"
known_ids[108] = "emblems/Perk Greed"
known_ids[109] = "emblems/Danger Close"
known_ids[110] = "emblems/Overkill"
known_ids[111] = "emblems/Gunfighter"
known_ids[112] = "emblems/Killjoy"
known_ids[113] = "emblems/Pest Control"
known_ids[114] = "emblems/Drones Eliminated"
known_ids[115] = "emblems/Dog Pound"
known_ids[117] = "emblems/Opportunistic"
known_ids[118] = "emblems/Maximum Payload"
known_ids[119] = "emblems/Anti-Swatter"
known_ids[120] = "emblems/Threat Neutralized"
known_ids[121] = "emblems/Special Delivery"
known_ids[122] = "emblems/RC Multi Bomber"
known_ids[123] = "emblems/Heavy Cover"
known_ids[124] = "emblems/Thumper"
known_ids[125] = "emblems/Shredder"
known_ids[126] = "emblems/Focus Fire"
known_ids[127] = "emblems/Tracker"
known_ids[129] = "emblems/Hard Counter"
known_ids[130] = "emblems/Overcooked"
known_ids[131] = "emblems/Cancelled Out"
known_ids[132] = "emblems/Make It Rain"
known_ids[133] = "emblems/Got Your Back"
known_ids[134] = "emblems/Small Game Hunter"
known_ids[135] = "emblems/Big Game Hunter"

# Block 2 (253-259) - completes the emblems category (all 106 shapes now
# confirmed: 38-136 + 253-259).
known_ids[253] = "emblems/Merciless"
known_ids[254] = "emblems/Ruthless"
known_ids[255] = "emblems/Hard to Kill"
known_ids[256] = "emblems/Invincible"
known_ids[257] = "emblems/Elite Member"
known_ids[258] = "emblems/Elite Founder"
