"""Static learning content for the hub.

Sources:
- Wilton Test Pack v3.1 (Test-Route-Pack-New.pdf): route maps, bonnet checks,
  weather and theory questions, fault grading.
- Driving test manoeuvres PDF: turn in the road and reverse around a corner.
- Driving information booklet (RSA): EDT / licence process.

Route summaries were read off the route maps. The maps in assets/routes are the
reference; the text here is a quick index to them.
"""

from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

# --------------------------------------------------------------------------- #
# External links
# --------------------------------------------------------------------------- #
LINKS = {
    "Book or manage a driving test": "https://www.drivingtest.ie",
    "Book a theory test": "https://www.theorytest.ie",
    "Learner permit and licence (NDLS)": "https://www.ndls.ie",
    "Road Safety Authority (EDT, ADI register)": "https://www.rsa.ie",
}

# --------------------------------------------------------------------------- #
# EDT and the RSA test
# --------------------------------------------------------------------------- #
EDT_LESSONS = [
    (1, "Car controls and safety checks", "Cockpit drill, controls, moving off and stopping."),
    (2, "Correct positioning", "Road position on the straight, at bends and junctions."),
    (3, "Changing direction", "Turning left and right, lane changes, roundabouts."),
    (4, "Progression management", "Smooth progress, gear choice, keeping up with traffic."),
    (5, "Coping with traffic", "Busier roads, queues, traffic lights and lanes."),
    (6, "Driving safely through traffic", "Planning ahead in urban traffic."),
    (7, "Speed management", "Speed limits, following distance, the two-second rule."),
    (8, "Sharing the road", "Pedestrians, cyclists, motorcyclists and large vehicles."),
    (9, "Hazard perception", "Spotting developing hazards early."),
    (10, "Anticipation and reaction", "Planning a response before you need it."),
    (11, "Driving on different road types", "Rural, national and dual-carriageway roads."),
    (12, "Night driving and adverse conditions", "Lights, glare, rain, fog and ice."),
]

EDT_FACTS = [
    "Required for anyone who took out a first car learner permit on or after 4 April 2011.",
    "12 one-hour lessons with an RSA Approved Driving Instructor (ADI).",
    "Your ADI stamps your logbook and records each lesson. Check that they appear on My EDT at rsa.ie.",
    "Practise with your sponsor between lessons. A sponsor is an experienced driver who holds a full licence.",
    "You need at least six months on your learner permit, and all 12 lessons done, before you can sit the test.",
]

TEST_STRUCTURE = [
    ("Arrive and check in", "Bring your learner permit. The car must be roadworthy, taxed, insured and showing L-plates."),
    ("Rules of the road", "Questions on road signs, road markings and the rules of the road."),
    ("Technical checks", "Tell the tester how you would check tyres, lights, oil, coolant, brake fluid and washer fluid. Some checks need the bonnet open."),
    ("Hand signals", "Show the arm signals for turning left, turning right and slowing down."),
    ("On-road drive", "About 30 to 40 minutes of everyday driving on one of the test routes."),
    ("Manoeuvres", "Reverse around a corner, turnabout (turn in the road) and hill start, done during the drive."),
    ("Result", "The tester explains your result and gives you a report on any faults."),
]

FAULT_GRADES = [
    ("Grade 1", "Minor", "Does not lead to a fail on its own.", "#3F7D3A"),
    ("Grade 2", "More serious", "Too many in total, or too many under one heading, is a fail.", "#B7791F"),
    ("Grade 3", "Dangerous or potentially dangerous", "A single Grade 3 fault is a fail.", "#B42318"),
]

# --------------------------------------------------------------------------- #
# Wilton test routes
# H = hill start, T = turnabout, R = reverse around a corner (as marked on maps)
# --------------------------------------------------------------------------- #
ROUTE_AREAS = ["Wilton", "Bishopstown", "Model Farm Road", "Glasheen", "Togher", "Pouladuff", "Ballyphehane", "Turners Cross"]

ROUTES = {
    1: {
        "areas": ["Wilton", "Glasheen", "Togher", "Pouladuff", "Ballyphehane"],
        "roads": ["Sarsfield Road", "Summerstown", "Togher Road", "Edward Walsh Road", "Pearse Road", "Vicar's Road", "Doughcloyne Road"],
        "hill": "Kilreendowney, off Pearse Road",
        "turn": "Joe Murphy Road area, Ballyphehane",
        "reverse": "Off Edward Walsh Road",
    },
    2: {
        "areas": ["Wilton", "Bishopstown", "Togher"],
        "roads": ["South Ring Road (N40)", "Togher Road", "Sarsfield Road", "Summerstown Road", "Bishopstown Road", "Doughcloyne Road"],
        "hill": "Woodbrook area, Bishopstown",
        "turn": "Summerstown Road, Wilton",
        "reverse": "Woodbrook area, Bishopstown",
    },
    3: {
        "areas": ["Bishopstown", "Model Farm Road", "Wilton"],
        "roads": ["Sarsfield Road", "Bishopstown Road", "Model Farm Road (R608)", "Rossa Avenue", "Melbourn Road", "Curraheen Road", "South Ring Road (N40)"],
        "hill": "Uam Var, off Rossa Avenue",
        "turn": "Melbourn Road",
        "reverse": "Uam Var, off Rossa Avenue",
    },
    4: {
        "areas": ["Wilton", "Bishopstown"],
        "roads": ["Sarsfield Road", "Leslie's Cross", "Summerstown", "Bishopstown Road", "Westgate Road", "Central Avenue", "Firgrove"],
        "hill": "Central Avenue / Wilton Avenue",
        "turn": "Westgate Road, off Curraheen Road",
        "reverse": "Summerstown, Wilton",
    },
    5: {
        "areas": ["Togher", "Pouladuff", "Ballyphehane"],
        "roads": ["Sarsfield Road", "Doughcloyne Road", "Togher Road", "Greenwood Estate", "Pouladuff Road", "Pearse Road", "Tramore Road", "South Ring Road (N40)"],
        "hill": "Doughcloyne Road",
        "turn": "Off Tramore Road",
        "reverse": "Greenwood Estate, Togher",
    },
    6: {
        "areas": ["Glasheen", "Togher", "Pouladuff"],
        "roads": ["Glasheen Road", "Clashduv", "Pouladuff Road", "Togher Road", "Doughcloyne Road", "Sarsfield Road"],
        "hill": "Doughcloyne Road",
        "turn": "Togher Road, near St Finbarr's",
        "reverse": "Sarsfield Court industrial estate",
    },
    7: {
        "areas": ["Glasheen", "Togher", "Pouladuff", "Ballyphehane"],
        "roads": ["Sarsfield Road", "Togher Road", "Elm Road", "Earlwood Estate", "Pearse Road", "Pouladuff Road", "South Ring Road (N40)"],
        "hill": "Elm Road / Hazel Road",
        "turn": "Earlwood Estate",
        "reverse": "Deanrock, Togher",
    },
    8: {
        "areas": ["Bishopstown", "Model Farm Road", "Wilton"],
        "roads": ["Sarsfield Road", "Bishopstown Road", "Rossa Avenue", "Uam Var", "Halldene", "Melbourn Road", "Waterfall Road", "South Ring Road (N40)"],
        "hill": "Not marked on this map",
        "turn": "Not marked on this map",
        "reverse": "Not marked on this map",
    },
    9: {
        "areas": ["Togher", "Pouladuff", "Ballyphehane", "Turners Cross"],
        "roads": ["Sarsfield Road", "Doughcloyne Road", "Togher Road", "Pouladuff Road", "Pearse Road", "Tory Top Road", "Kinsale Road", "South Ring Road (N40)"],
        "hill": "Near Turners Cross",
        "turn": "Greenwood Estate, Togher",
        "reverse": "Greenwood Estate, Togher",
    },
    10: {
        "areas": ["Bishopstown", "Model Farm Road", "Wilton"],
        "roads": ["Sarsfield Road", "Bishopstown Road", "Rossa Avenue", "Melbourn Road", "Westgate Road", "Firgrove", "Woodbrook"],
        "hill": "Melbourn Avenue / Westgate Road",
        "turn": "Firgrove Drive / Westgate Road",
        "reverse": "Woodbrook Grove",
    },
}


def route_image(number: int) -> Path:
    return ASSETS_DIR / "routes" / f"route_{number:02d}.jpg"


# --------------------------------------------------------------------------- #
# Technical checks (Wilton Test Pack, bonnet check questions)
# --------------------------------------------------------------------------- #
BONNET_CHECKS = [
    (
        "Engine oil",
        "Dipstick",
        "Remove the dipstick and wipe the end with a clean cloth. Put it back, take it out again, "
        "and check the oil sits between the minimum and maximum marks.",
    ),
    (
        "Brake fluid",
        "Brake fluid reservoir",
        "The fluid must show between the minimum and maximum marks on the side of the reservoir.",
    ),
    (
        "Engine coolant",
        "Coolant reservoir",
        "The coolant must show between the minimum and maximum marks on the side of the reservoir. "
        "Only check it with the engine cold.",
    ),
    (
        "Windscreen washer",
        "Washer reservoir",
        "The reservoir has no external marks. Remove the cap and look at the level. Top it up with "
        "water and screenwash additive (not anti-freeze).",
    ),
]

IN_CAR_CHECKS = [
    (
        "How do you check the footbrake works before a journey?",
        "The brakes should not feel spongy or pull to one side. Test them as soon as you pull away, where it is safe.",
    ),
    (
        "How do you check the brake lights work?",
        "Press the brake pedal while you can see a reflection of the back of the car, such as a shop window, or ask someone to watch.",
    ),
    (
        "How do you check the indicators on your own?",
        "Switch on one indicator and walk around the car. Then switch to the other side and check again.",
    ),
    (
        "How would you know an indicator bulb has failed while driving?",
        "The indicator clicks at about twice the normal speed when you select the side with the failed bulb.",
    ),
    (
        "How do you know your tyres are safe and legal?",
        "Tread depth of at least 1.6 mm, pressures set to the manufacturer's figures, and no cuts, cracks or bulges.",
    ),
    (
        "How does a front-tyre puncture affect the steering?",
        "The steering pulls towards the flat tyre.",
    ),
    (
        "How can you check the handbrake safely?",
        "On a flat surface, select first gear with the handbrake on and slowly raise the clutch. The handbrake should hold the car and stall the engine.",
    ),
]

THEORY_QUESTIONS = [
    ("When can you overtake on the left?", "When the driver in front is turning right, when you intend to turn left, or when traffic in the lane to your right is moving more slowly in queues."),
    ("At an uncontrolled junction of equal importance, who do you give way to?", "Traffic on your right, and traffic already turning."),
    ("At a stop sign with no white line, where do you stop?", "At the stop sign."),
    ("How do you recognise a zebra crossing at night?", "By the flashing yellow beacons."),
    ("When must you not use the horn?", "Between 11.30 pm and 7.00 am in a built-up area, except in an emergency."),
    ("When should you dip your headlights?", "When meeting oncoming traffic, when following close behind another vehicle, on continuously lit roads, and in snow, fog, dusk or dawn."),
    ("What is a clearway?", "Stopping or parking is not allowed (except buses and taxis) during the times shown on the sign."),
    ("What does a single yellow line mean?", "No parking at certain times."),
    ("How close to a junction can you park?", "No closer than 5 metres."),
    ("What is the two-second rule?", "Stay at least two seconds behind the vehicle in front. Count from when it passes a fixed object."),
    ("What does a red triangle on the road mean?", "There is an obstruction on the road ahead."),
    ("Who in authority must you stop for?", "A Garda, a school warden, or a person in charge of animals."),
    ("What are the speed limits on national roads, motorways and in built-up areas?", "100 km/h on national roads, 120 km/h on motorways, 50 km/h in built-up areas, unless signs show otherwise."),
    ("What is the legal minimum tyre tread depth?", "1.6 mm."),
    ("What are the rules for a yellow box junction?", "Do not enter unless your exit is clear. You may wait in it to turn right if you are not blocking other traffic."),
    ("When can you cross a continuous white line?", "To avoid an obstruction, for access, or when there is a broken white line on your side."),
    ("What do two sets of broken white lines in the centre of the road mean?", "One or two continuous white lines are coming up ahead."),
    ("What do white diagonal lines in the centre of the road mean?", "Treat them like a traffic island and do not drive on them."),
]

# --------------------------------------------------------------------------- #
# Manoeuvres
# --------------------------------------------------------------------------- #
MANOEUVRES = {
    "Turn in the road (turnabout)": {
        "image": ASSETS_DIR / "manoeuvres" / "turn_in_the_road.jpg",
        "summary": "Turn the car to face the other way using forward and reverse gears, as few moves as possible, without touching the kerb.",
        "steps": [
            ("Position 1 to 2", [
                "Prepare, observe, move (P.O.M.).",
                "Creep forward very slowly for half a metre, then make a final blind-spot check.",
                "Steer briskly to full right lock.",
                "Near the far kerb, steer briskly left.",
                "Check your reference point, clutch down and brake to stop. Secure the car.",
            ]),
            ("Position 2 to 3", [
                "P.O.M., then look through the rear window.",
                "Release the handbrake and steer briskly left.",
                "Look over your left shoulder. Halfway across, steer right.",
                "Check over your right shoulder and your reference point. Clutch down and brake to stop. Secure the car.",
            ]),
            ("Position 3 to 4", [
                "P.O.M., then steer briskly right.",
                "Check your clearance from the kerb. Reverse again only if you need to.",
                "Pull up or drive on, using mirror, signal, manoeuvre (M.S.M.).",
            ]),
        ],
        "key_points": [
            "Control: very slow speed, good pedal coordination, brisk steering.",
            "Observation: look all round and react to other road users.",
            "Accuracy: stop close to the kerb without touching or overhanging it.",
        ],
    },
    "Reverse around a corner": {
        "image": ASSETS_DIR / "manoeuvres" / "reverse_around_corner.jpg",
        "summary": "Reverse left into a side road and continue straight back for three to four car lengths, staying close and parallel to the kerb.",
        "steps": [
            ("Set up", [
                "Mirror, signal, manoeuvre (M.S.M.) and look into the side road as you pass it.",
                "Stop about a drain's width (30 to 45 cm) from the kerb, parallel to it.",
                "P.O.M. before you move off in reverse.",
            ]),
            ("Into the corner", [
                "Keep the steering straight until your reference point reaches the start of the bend.",
                "Steer left to follow the kerb. The front of the car will swing out, so check over your right shoulder at the point of turn.",
                "Glance in the nearside mirror to keep your distance from the kerb.",
            ]),
            ("Finish", [
                "Straighten up and continue back three to four car lengths.",
                "If you drift, pull forward to correct it. Do not touch the kerb.",
            ]),
        ],
        "key_points": [
            "Control: set the gas, use the clutch to stay at a crawl, and do not lift the clutch and brake together.",
            "Observation: look all round throughout. Stop for pedestrians, children and other traffic.",
            "Accuracy: stay reasonably close and parallel to the kerb.",
        ],
    },
    "Hill start": {
        "image": None,
        "summary": "Move off on an uphill slope without rolling back, stalling or over-revving.",
        "steps": [
            ("Prepare", [
                "Clutch down, select first gear.",
                "Set a little more gas than on the flat.",
                "Raise the clutch slowly to the biting point and hold it there.",
            ]),
            ("Observe", [
                "Check your mirrors and look over your right shoulder for the blind spot.",
                "Signal if another road user would benefit.",
            ]),
            ("Move", [
                "Release the handbrake. The car should hold or creep forward, not roll back.",
                "Raise the clutch slowly and add gas as you pull away.",
                "If the car starts to roll back, put the handbrake back on and start again.",
            ]),
        ],
        "key_points": [
            "No rolling back. The tester watches for this closely.",
            "Do not over-rev or ride the clutch.",
            "Observation before moving off counts as much as control.",
        ],
    },
}

EXTRA_DIAGRAMS = {
    "Roundabouts": ASSETS_DIR / "manoeuvres" / "roundabouts.jpg",
    "Hand signals": ASSETS_DIR / "manoeuvres" / "hand_signals.jpg",
}

FAULT_GUIDE_IMAGES = [ASSETS_DIR / "checks" / f"fault_guidelines_{n}.jpg" for n in (1, 2, 3)]
BONNET_IMAGE = ASSETS_DIR / "checks" / "bonnet_locations.jpg"

# --------------------------------------------------------------------------- #
# Approved Driving Instructors, County Cork (from the project ADI directory)
# lat/lon are approximate area centres for the map, not business addresses.
# edt=False means EDT is not listed for that entry, not that it is unavailable.
# --------------------------------------------------------------------------- #
ADI_DIRECTORY = [
    {"area": "Ballincollig", "instructor": "Patrick Linehan", "services": "Manual, EDT, test prep", "transmission": "Manual", "edt": True, "lat": 51.888, "lon": -8.592},
    {"area": "Ballyvolane", "instructor": "Bríd Boag", "services": "Manual and automatic, EDT", "transmission": "Manual & automatic", "edt": True, "lat": 51.918, "lon": -8.457},
    {"area": "Blackrock / Mahon", "instructor": "Paul O'Halloran", "services": "Automatic lessons", "transmission": "Automatic", "edt": False, "lat": 51.895, "lon": -8.400},
    {"area": "Douglas", "instructor": "Local ADI Team", "services": "12-lesson EDT", "transmission": "Not stated", "edt": True, "lat": 51.877, "lon": -8.437},
    {"area": "Mallow", "instructor": "Pat Linehan & Team", "services": "Test route prep", "transmission": "Not stated", "edt": False, "lat": 52.139, "lon": -8.645},
    {"area": "Midleton / East Cork", "instructor": "Market Green Instructors", "services": "Manual and automatic", "transmission": "Manual & automatic", "edt": False, "lat": 51.916, "lon": -8.175},
    {"area": "Wilton / Togher", "instructor": "Wilton Test Centre Instructors", "services": "Specialised test routes", "transmission": "Not stated", "edt": False, "lat": 51.884, "lon": -8.506},
]
