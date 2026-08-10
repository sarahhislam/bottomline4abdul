"""
Supporter Map backend for the Global Bulletin Board page.
Provides:
  - Persistent JSON storage of supporter pins
  - Type-ahead city/country database with approximate lat/lng
  - Expanded vibe badge definitions
  - API handler functions for GET (list) and POST (add)
"""
import json
import os
import uuid
import time

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'supporters_data.json')

# ─── Expanded Vibe Badges ───
VIBES = {
    # Academics, STEM & General Engineering
    "First Principles": {"emoji": "📐", "color": "#406bbf", "category": "Academics & STEM"},
    "Lab Bench & Code": {"emoji": "🔬", "color": "#6c5ce7", "category": "Academics & STEM"},
    "Study Hall Regular": {"emoji": "📚", "color": "#0984e3", "category": "Academics & STEM"},
    "Briefcase & Books": {"emoji": "⚖️", "color": "#b2bec3", "category": "Academics & STEM"},
    "Policy Wonk": {"emoji": "📋", "color": "#2d3436", "category": "Academics & STEM"},
    "Data Driven": {"emoji": "📊", "color": "#00b894", "category": "Academics & STEM"},
    "Public Health Minded": {"emoji": "🩺", "color": "#e17055", "category": "Academics & STEM"},
    "Epidemiology Nerd": {"emoji": "🧬", "color": "#6c5ce7", "category": "Academics & STEM"},
    # Sports & Racing Culture
    "Paddock Pass": {"emoji": "🏁", "color": "#d21214", "category": "Sports & Racing"},
    "Apex Predator": {"emoji": "⏱️", "color": "#e17055", "category": "Sports & Racing"},
    "Supporters Section": {"emoji": "⚽", "color": "#00b894", "category": "Sports & Racing"},
    "Hardwood Historian": {"emoji": "🏀", "color": "#e84393", "category": "Sports & Racing"},
    "Matchday Energy": {"emoji": "🏟️", "color": "#fdcb6e", "category": "Sports & Racing"},
    "Lions Roar": {"emoji": "🦁", "color": "#0076b6", "category": "Sports & Racing"},
    "Winged Wheel": {"emoji": "🏒", "color": "#d21214", "category": "Sports & Racing"},
    "Motor City Speed": {"emoji": "🏎️", "color": "#e17055", "category": "Sports & Racing"},
    "Tailgate Captain": {"emoji": "🍔", "color": "#fdcb6e", "category": "Sports & Racing"},
    # Culture, Arts & Daily Life
    "Third Wave Espresso": {"emoji": "☕", "color": "#a0522d", "category": "Culture & Arts"},
    "Headphones In": {"emoji": "🎧", "color": "#636e72", "category": "Culture & Arts"},
    "Canvas & Code": {"emoji": "🎨", "color": "#e056fd", "category": "Culture & Arts"},
    "Rooted & Grounded": {"emoji": "🌱", "color": "#2e7d32", "category": "Culture & Arts"},
    "Night Owl Shift": {"emoji": "🌙", "color": "#2d3436", "category": "Culture & Arts"},
    "Sunday Service": {"emoji": "🕌", "color": "#0984e3", "category": "Culture & Arts"},
    "Halaqa Circle": {"emoji": "📖", "color": "#2e7d32", "category": "Culture & Arts"},
    "Family Table": {"emoji": "🍽️", "color": "#e17055", "category": "Culture & Arts"},
    "Community Kitchen": {"emoji": "🍲", "color": "#d63031", "category": "Culture & Arts"},
    "Book Club Regular": {"emoji": "📚", "color": "#6c5ce7", "category": "Culture & Arts"},
    "Vinyl & Vintage": {"emoji": "💿", "color": "#e84393", "category": "Culture & Arts"},
    "Garden Grown": {"emoji": "🌻", "color": "#fdcb6e", "category": "Culture & Arts"},
    # Global & General Movement
    "Out of District": {"emoji": "🗺️", "color": "#00cec9", "category": "Global Movement"},
    "Transit Lounge": {"emoji": "✈️", "color": "#74b9ff", "category": "Global Movement"},
    "Global Grid": {"emoji": "🌍", "color": "#e68a00", "category": "Global Movement"},
    "Diaspora Dreamer": {"emoji": "🌉", "color": "#6c5ce7", "category": "Global Movement"},
    "New American": {"emoji": "🗽", "color": "#0984e3", "category": "Global Movement"},
    "Returning Home": {"emoji": "🏡", "color": "#2e7d32", "category": "Global Movement"},
    "Borderless Believer": {"emoji": "🕊️", "color": "#74b9ff", "category": "Global Movement"},
    "Midnight Caller": {"emoji": "📞", "color": "#2d3436", "category": "Global Movement"},
    # Michigan Roots & Community
    "Pure Michigan": {"emoji": "🌊", "color": "#00b894", "category": "Michigan Roots"},
    "Motor City": {"emoji": "🚗", "color": "#d21214", "category": "Michigan Roots"},
    "Up North": {"emoji": "🌲", "color": "#2e7d32", "category": "Michigan Roots"},
    "Downriver": {"emoji": "⛴️", "color": "#0984e3", "category": "Michigan Roots"},
    "Lake Life": {"emoji": "⛵", "color": "#00cec9", "category": "Michigan Roots"},
    "Farm Fresh": {"emoji": "🚜", "color": "#fdcb6e", "category": "Michigan Roots"},
    "Cherry Capital": {"emoji": "🍒", "color": "#d63031", "category": "Michigan Roots"},
    "Coney Dog Classic": {"emoji": "🌭", "color": "#e17055", "category": "Michigan Roots"},
    "Great Lakes State": {"emoji": "💧", "color": "#74b9ff", "category": "Michigan Roots"},
    # Campaign Crew & Volunteer
    "Door Knocker": {"emoji": "🚪", "color": "#e17055", "category": "Campaign Crew"},
    "Phone Banker": {"emoji": "📱", "color": "#0984e3", "category": "Campaign Crew"},
    "Text Banker": {"emoji": "💬", "color": "#00b894", "category": "Campaign Crew"},
    "Volunteer Captain": {"emoji": "🧭", "color": "#d21214", "category": "Campaign Crew"},
    "First Time Voter": {"emoji": "🗳️", "color": "#6c5ce7", "category": "Campaign Crew"},
    "Election Day Ready": {"emoji": "✅", "color": "#2e7d32", "category": "Campaign Crew"},
    "Yard Sign Squad": {"emoji": "🪧", "color": "#fdcb6e", "category": "Campaign Crew"},
    "Sticker Slinger": {"emoji": "🏷️", "color": "#e84393", "category": "Campaign Crew"},
    "Rally Regular": {"emoji": "📣", "color": "#d21214", "category": "Campaign Crew"},
    "Neighborhood Organizer": {"emoji": "🤝", "color": "#00cec9", "category": "Campaign Crew"},
    "Union Strong": {"emoji": "✊", "color": "#d63031", "category": "Campaign Crew"},
    "Teacher's Pet": {"emoji": "🍎", "color": "#e17055", "category": "Campaign Crew"},
    "Nurse on Duty": {"emoji": "💉", "color": "#74b9ff", "category": "Campaign Crew"},
    "Small Biz Owner": {"emoji": "🏪", "color": "#fdcb6e", "category": "Campaign Crew"},
}

# ─── Type-ahead City/Country Database (city, country, lat, lng) ───
CITY_DB = [
    # Michigan
    ("Detroit", "USA", 42.3314, -83.0458),
    ("Dearborn", "USA", 42.3223, -83.1763),
    ("Ann Arbor", "USA", 42.2808, -83.7430),
    ("Grand Rapids", "USA", 42.9634, -85.6681),
    ("Lansing", "USA", 42.7325, -84.5555),
    ("Flint", "USA", 43.0125, -83.6875),
    ("Kalamazoo", "USA", 42.2917, -85.5872),
    ("Traverse City", "USA", 44.7631, -85.6206),
    ("Hamtramck", "USA", 42.3928, -83.0496),
    ("Warren", "USA", 42.5145, -83.0147),
    ("Sterling Heights", "USA", 42.5803, -83.0302),
    ("Troy", "USA", 42.6064, -83.1497),
    ("Farmington Hills", "USA", 42.4989, -83.3733),
    ("Pontiac", "USA", 42.6389, -83.2910),
    ("Southfield", "USA", 42.4734, -83.2219),
    ("Royal Oak", "USA", 42.4895, -83.1446),
    ("Dearborn Heights", "USA", 42.3369, -83.2738),
    ("Livonia", "USA", 42.3684, -83.3527),
    ("Canton", "USA", 42.3086, -83.4822),
    ("Novi", "USA", 42.4806, -83.4755),
    ("West Bloomfield", "USA", 42.5689, -83.3836),
    ("Bloomfield Hills", "USA", 42.5836, -83.2455),
    ("Rochester Hills", "USA", 42.6584, -83.1499),
    ("Macomb", "USA", 42.7009, -82.9327),
    ("Clinton Township", "USA", 42.5869, -82.9194),
    ("East Lansing", "USA", 42.7369, -84.4839),
    ("Saginaw", "USA", 43.4195, -83.9508),
    ("Bay City", "USA", 43.5945, -83.8889),
    ("Midland", "USA", 43.6156, -84.2472),
    ("Muskegon", "USA", 43.2342, -86.2484),
    ("Jackson", "USA", 42.2459, -84.4013),
    ("Battle Creek", "USA", 42.3212, -85.1797),
    ("Benton Harbor", "USA", 42.1167, -86.4542),
    ("Port Huron", "USA", 42.9709, -82.4249),
    ("Marquette", "USA", 46.5476, -87.3958),
    ("Sault Ste. Marie", "USA", 46.4953, -84.3453),
    ("Holland", "USA", 42.7875, -86.1089),
    ("Wyoming", "USA", 42.9134, -85.7053),
    ("Kentwood", "USA", 42.8695, -85.6447),
    ("Taylor", "USA", 42.2409, -83.2697),
    ("Allen Park", "USA", 42.2575, -83.2110),
    ("Lincoln Park", "USA", 42.2506, -83.1785),
    ("Melvindale", "USA", 42.2825, -83.1752),
    ("Garden City", "USA", 42.3256, -83.3310),
    ("Inkster", "USA", 42.2942, -83.3099),
    ("Wayne", "USA", 42.2814, -83.3863),
    ("Westland", "USA", 42.3242, -83.4002),
    ("Redford", "USA", 42.3834, -83.2966),
    ("Oak Park", "USA", 42.4595, -83.1827),
    ("Ferndale", "USA", 42.4606, -83.1346),
    ("Hazel Park", "USA", 42.4625, -83.1041),
    ("Madison Heights", "USA", 42.4859, -83.1052),
    ("Berkley", "USA", 42.5031, -83.1835),
    ("Huntington Woods", "USA", 42.4806, -83.1674),
    ("Pleasant Ridge", "USA", 42.4711, -83.1427),
    ("Clawson", "USA", 42.5334, -83.1463),
    ("Birmingham", "USA", 42.5467, -83.2113),
    ("Franklin", "USA", 42.5167, -83.3055),
    ("South Lyon", "USA", 42.4606, -83.6516),
    ("Brighton", "USA", 42.5295, -83.7802),
    ("Howell", "USA", 42.6073, -83.9294),
    ("Fenton", "USA", 42.7978, -83.7049),
    ("Grand Blanc", "USA", 42.9275, -83.6299),
    ("Burton", "USA", 42.9995, -83.6161),
    ("Mount Pleasant", "USA", 43.5978, -84.7675),
    ("Alma", "USA", 43.3789, -84.6597),
    ("Owosso", "USA", 42.9978, -84.1766),
    ("Adrian", "USA", 41.8975, -84.0372),
    ("Tecumseh", "USA", 42.0039, -83.9449),
    ("Monroe", "USA", 41.9164, -83.3977),
    ("Trenton", "USA", 42.1395, -83.1783),
    ("Wyandotte", "USA", 42.2142, -83.1499),
    ("Riverview", "USA", 42.1742, -83.1794),
    ("Flat Rock", "USA", 42.0964, -83.2919),
    ("Woodhaven", "USA", 42.1389, -83.2416),
    ("Brownstown", "USA", 42.1289, -83.2249),
    ("Romulus", "USA", 42.2223, -83.3966),
    ("Belleville", "USA", 42.2048, -83.4852),
    ("Ypsilanti", "USA", 42.2441, -83.6129),
    ("Saline", "USA", 42.1667, -83.7819),
    ("Chelsea", "USA", 42.3181, -84.0205),
    ("Dexter", "USA", 42.3384, -83.8886),
    ("Milan", "USA", 42.0853, -83.6824),
    ("Plymouth", "USA", 42.3714, -83.4705),
    ("Northville", "USA", 42.4311, -83.4833),
    ("Wixom", "USA", 42.5248, -83.5366),
    ("Walled Lake", "USA", 42.5378, -83.4811),
    ("Commerce Township", "USA", 42.5911, -83.4908),
    ("Highland", "USA", 42.6467, -83.6005),
    ("Milford", "USA", 42.5903, -83.5997),
    ("White Lake", "USA", 42.6550, -83.4872),
    ("Waterford", "USA", 42.7023, -83.4027),
    ("Clarkston", "USA", 42.7359, -83.4188),
    ("Oxford", "USA", 42.8248, -83.2647),
    ("Lake Orion", "USA", 42.7845, -83.2397),
    ("Auburn Hills", "USA", 42.6875, -83.2341),
    ("Rochester", "USA", 42.6806, -83.1338),
    ("Utica", "USA", 42.6261, -83.0335),
    ("Shelby Township", "USA", 42.6711, -83.0327),
    ("Washington Township", "USA", 42.7242, -83.0363),
    ("Romeo", "USA", 42.8028, -83.0127),
    ("New Baltimore", "USA", 42.6811, -82.7369),
    ("Chesterfield", "USA", 42.6670, -82.8224),
    ("Harrison Township", "USA", 42.5873, -82.8288),
    ("Mount Clemens", "USA", 42.5973, -82.8780),
    ("Roseville", "USA", 42.4973, -82.9371),
    ("Eastpointe", "USA", 42.4684, -82.9555),
    ("Fraser", "USA", 42.5392, -82.9494),
    ("St. Clair Shores", "USA", 42.4973, -82.8888),
    ("Grosse Pointe", "USA", 42.3861, -82.9119),
    ("Grosse Pointe Woods", "USA", 42.4436, -82.9069),
    ("Harper Woods", "USA", 42.4331, -82.9241),
    ("Center Line", "USA", 42.4850, -83.0277),
    ("Warren", "USA", 42.5145, -83.0147),
    # USA
    ("New York", "USA", 40.7128, -74.0060),
    ("Chicago", "USA", 41.8781, -87.6298),
    ("Los Angeles", "USA", 34.0522, -118.2437),
    ("San Francisco", "USA", 37.7749, -122.4194),
    ("Austin", "USA", 30.2672, -97.7431),
    ("Seattle", "USA", 47.6062, -122.3321),
    ("Boston", "USA", 42.3601, -71.0589),
    ("Washington DC", "USA", 38.9072, -77.0369),
    ("Atlanta", "USA", 33.7490, -84.3880),
    ("Miami", "USA", 25.7617, -80.1918),
    ("Houston", "USA", 29.7604, -95.3698),
    ("Phoenix", "USA", 33.4484, -112.0740),
    ("Denver", "USA", 39.7392, -104.9903),
    ("Minneapolis", "USA", 44.9778, -93.2650),
    ("Nashville", "USA", 36.1627, -86.7816),
    ("Charlotte", "USA", 35.2271, -80.8431),
    ("Orlando", "USA", 28.5383, -81.3792),
    ("Las Vegas", "USA", 36.1699, -115.1398),
    ("San Diego", "USA", 32.7157, -117.1611),
    ("Dallas", "USA", 32.7767, -96.7970),
    ("Philadelphia", "USA", 39.9526, -75.1652),
    ("Cleveland", "USA", 41.4993, -81.6944),
    ("Columbus", "USA", 39.9612, -82.9988),
    ("Indianapolis", "USA", 39.7684, -86.1581),
    ("Milwaukee", "USA", 43.0389, -87.9065),
    ("St. Louis", "USA", 38.6270, -90.1994),
    ("New Orleans", "USA", 29.9511, -90.0715),
    ("Portland", "USA", 45.5152, -122.6784),
    ("Sacramento", "USA", 38.5816, -121.4944),
    ("San Jose", "USA", 37.3382, -121.8863),
    ("Baltimore", "USA", 39.2904, -76.6122),
    ("Pittsburgh", "USA", 40.4406, -79.9959),
    ("Tampa", "USA", 27.9506, -82.4572),
    ("Kansas City", "USA", 39.0997, -94.5786),
    ("Salt Lake City", "USA", 40.7608, -111.8910),
    ("Albuquerque", "USA", 35.0844, -106.6504),
    ("Oklahoma City", "USA", 35.4676, -97.5164),
    ("Memphis", "USA", 35.1495, -90.0490),
    ("Louisville", "USA", 38.2527, -85.7585),
    ("Cincinnati", "USA", 39.1031, -84.5120),
    ("Hartford", "USA", 41.7658, -72.6734),
    ("Providence", "USA", 41.8240, -71.4128),
    ("Madison", "USA", 43.0731, -89.4012),
    ("Raleigh", "USA", 35.7796, -78.6382),
    ("Durham", "USA", 35.9940, -78.8986),
    ("Richmond", "USA", 37.5407, -77.4360),
    ("Charleston", "USA", 32.7765, -79.9311),
    ("Savannah", "USA", 32.0809, -81.0912),
    ("Birmingham", "USA", 33.5186, -86.8104),
    ("Little Rock", "USA", 34.7465, -92.2896),
    ("Omaha", "USA", 41.2565, -95.9345),
    ("Des Moines", "USA", 41.5868, -93.6250),
    ("Boise", "USA", 43.6150, -116.2023),
    ("Spokane", "USA", 47.6588, -117.4260),
    ("Anchorage", "USA", 61.2181, -149.9003),
    ("Honolulu", "USA", 21.3069, -157.8583),
    # Canada
    ("Toronto", "Canada", 43.6532, -79.3832),
    ("Vancouver", "Canada", 49.2827, -123.1207),
    ("Montreal", "Canada", 45.5017, -73.5673),
    ("Ottawa", "Canada", 45.4215, -75.6972),
    ("Calgary", "Canada", 51.0447, -114.0719),
    ("Edmonton", "Canada", 53.5461, -113.4938),
    ("Windsor", "Canada", 42.3149, -83.0364),
    ("London", "Canada", 42.9849, -81.2453),
    ("Hamilton", "Canada", 43.2557, -79.8711),
    ("Waterloo", "Canada", 43.4643, -80.5204),
    # UK & Europe
    ("London", "UK", 51.5074, -0.1278),
    ("Paris", "France", 48.8566, 2.3522),
    ("Berlin", "Germany", 52.5200, 13.4050),
    ("Madrid", "Spain", 40.4168, -3.7038),
    ("Rome", "Italy", 41.9028, 12.4964),
    ("Amsterdam", "Netherlands", 52.3676, 4.9041),
    ("Warsaw", "Poland", 52.2297, 21.0122),
    ("Dublin", "Ireland", 53.3498, -6.2603),
    ("Lisbon", "Portugal", 38.7223, -9.1393),
    ("Stockholm", "Sweden", 59.3293, 18.0686),
    ("Oslo", "Norway", 59.9139, 10.7522),
    ("Copenhagen", "Denmark", 55.6761, 12.5683),
    ("Helsinki", "Finland", 60.1699, 24.9384),
    ("Vienna", "Austria", 48.2082, 16.3738),
    ("Prague", "Czech Republic", 50.0755, 14.4378),
    ("Budapest", "Hungary", 47.4979, 19.0402),
    ("Athens", "Greece", 37.9838, 23.7275),
    ("Brussels", "Belgium", 50.8503, 4.3517),
    ("Zurich", "Switzerland", 47.3769, 8.5417),
    ("Geneva", "Switzerland", 46.2044, 6.1432),
    ("Munich", "Germany", 48.1351, 11.5820),
    ("Frankfurt", "Germany", 50.1109, 8.6821),
    ("Barcelona", "Spain", 41.3874, 2.1686),
    ("Milan", "Italy", 45.4642, 9.1900),
    ("Naples", "Italy", 40.8518, 14.2681),
    ("Edinburgh", "UK", 55.9533, -3.1883),
    ("Manchester", "UK", 53.4808, -2.2426),
    ("Birmingham", "UK", 52.4862, -1.8904),
    ("Leeds", "UK", 53.8008, -1.5491),
    ("Glasgow", "UK", 55.8642, -4.2518),
    ("Belfast", "UK", 54.5973, -5.9301),
    ("Cardiff", "UK", 51.4816, -3.1791),
    # Middle East
    ("Dubai", "UAE", 25.2048, 55.2708),
    ("Abu Dhabi", "UAE", 24.4539, 54.3773),
    ("Sharjah", "UAE", 25.3463, 55.4209),
    ("Riyadh", "Saudi Arabia", 24.7136, 46.6753),
    ("Jeddah", "Saudi Arabia", 21.4858, 39.1925),
    ("Mecca", "Saudi Arabia", 21.3891, 39.8579),
    ("Medina", "Saudi Arabia", 24.5247, 39.5692),
    ("Dammam", "Saudi Arabia", 26.4207, 50.0888),
    ("Istanbul", "Turkey", 41.0082, 28.9784),
    ("Ankara", "Turkey", 39.9334, 32.8597),
    ("Izmir", "Turkey", 38.4237, 27.1428),
    ("Tehran", "Iran", 35.6892, 51.3890),
    ("Mashhad", "Iran", 36.2605, 59.6168),
    ("Baghdad", "Iraq", 33.3152, 44.3661),
    ("Basra", "Iraq", 30.5081, 47.7805),
    ("Erbil", "Iraq", 36.1911, 44.0092),
    ("Mosul", "Iraq", 36.3350, 43.1189),
    ("Amman", "Jordan", 31.9454, 35.9284),
    ("Beirut", "Lebanon", 33.8938, 35.5018),
    ("Damascus", "Syria", 33.5138, 36.2765),
    ("Aleppo", "Syria", 36.2021, 37.1343),
    ("Tel Aviv", "Israel", 32.0853, 34.7818),
    ("Jerusalem", "Israel", 31.7683, 35.2137),
    ("Haifa", "Israel", 32.7940, 34.9896),
    ("Gaza", "Palestine", 31.5017, 34.4668),
    ("Ramallah", "Palestine", 31.9038, 35.2034),
    ("Nablus", "Palestine", 32.2211, 35.2544),
    ("Hebron", "Palestine", 31.5326, 35.0998),
    ("Bethlehem", "Palestine", 31.7054, 35.2024),
    ("Doha", "Qatar", 25.2854, 51.5310),
    ("Kuwait City", "Kuwait", 29.3759, 47.9774),
    ("Manama", "Bahrain", 26.2285, 50.5860),
    ("Muscat", "Oman", 23.5880, 58.3829),
    ("Sana'a", "Yemen", 15.3694, 44.1910),
    ("Cairo", "Egypt", 30.0444, 31.2357),
    # South & Central Asia
    ("Karachi", "Pakistan", 24.8607, 67.0011),
    ("Lahore", "Pakistan", 31.5204, 74.3587),
    ("Islamabad", "Pakistan", 33.6844, 73.0479),
    ("Rawalpindi", "Pakistan", 33.5651, 73.0169),
    ("Faisalabad", "Pakistan", 31.4504, 73.1350),
    ("Peshawar", "Pakistan", 34.0151, 71.5249),
    ("Quetta", "Pakistan", 30.1798, 66.9750),
    ("Mumbai", "India", 19.0760, 72.8777),
    ("New Delhi", "India", 28.6139, 77.2090),
    ("Kolkata", "India", 22.5726, 88.3639),
    ("Chennai", "India", 13.0827, 80.2707),
    ("Hyderabad", "India", 17.3850, 78.4867),
    ("Bengaluru", "India", 12.9716, 77.5946),
    ("Ahmedabad", "India", 23.0225, 72.5714),
    ("Pune", "India", 18.5204, 73.8567),
    ("Jaipur", "India", 26.9124, 75.7873),
    ("Lucknow", "India", 26.8467, 80.9462),
    ("Dhaka", "Bangladesh", 23.8103, 90.4125),
    ("Chittagong", "Bangladesh", 22.3569, 91.7832),
    ("Kabul", "Afghanistan", 34.5553, 69.2075),
    ("Herat", "Afghanistan", 34.3529, 62.2040),
    ("Tashkent", "Uzbekistan", 41.2995, 69.2401),
    ("Samarkand", "Uzbekistan", 39.6270, 66.9750),
    ("Almaty", "Kazakhstan", 43.2220, 76.8512),
    ("Astana", "Kazakhstan", 51.1605, 71.4704),
    ("Baku", "Azerbaijan", 40.4093, 49.8671),
    ("Tbilisi", "Georgia", 41.7151, 44.8271),
    ("Yerevan", "Armenia", 40.1792, 44.4991),
    ("Bishkek", "Kyrgyzstan", 42.8746, 74.5698),
    ("Dushanbe", "Tajikistan", 38.5598, 68.7870),
    ("Ashgabat", "Turkmenistan", 37.9601, 58.3261),
    # East & Southeast Asia
    ("Tokyo", "Japan", 35.6762, 139.6503),
    ("Osaka", "Japan", 34.6937, 135.5023),
    ("Kyoto", "Japan", 35.0116, 135.7681),
    ("Nagoya", "Japan", 35.1815, 136.9066),
    ("Seoul", "South Korea", 37.5665, 126.9780),
    ("Busan", "South Korea", 35.1796, 129.0756),
    ("Beijing", "China", 39.9042, 116.4074),
    ("Shanghai", "China", 31.2304, 121.4737),
    ("Hong Kong", "China", 22.3193, 114.1694),
    ("Guangzhou", "China", 23.1291, 113.2644),
    ("Shenzhen", "China", 22.5431, 114.0579),
    ("Taipei", "Taiwan", 25.0330, 121.5654),
    ("Singapore", "Singapore", 1.3521, 103.8198),
    ("Kuala Lumpur", "Malaysia", 3.1390, 101.6869),
    ("Penang", "Malaysia", 5.4164, 100.3327),
    ("Jakarta", "Indonesia", -6.2088, 106.8456),
    ("Surabaya", "Indonesia", -7.2575, 112.7521),
    ("Bangkok", "Thailand", 13.7563, 100.5018),
    ("Manila", "Philippines", 14.5995, 120.9842),
    ("Quezon City", "Philippines", 14.6760, 121.0437),
    ("Ho Chi Minh City", "Vietnam", 10.8231, 106.6297),
    ("Hanoi", "Vietnam", 21.0278, 105.8342),
    ("Phnom Penh", "Cambodia", 11.5564, 104.9282),
    ("Yangon", "Myanmar", 16.8409, 96.1735),
    ("Kathmandu", "Nepal", 27.7172, 85.3240),
    ("Colombo", "Sri Lanka", 6.9271, 79.8612),
    ("Ulaanbaatar", "Mongolia", 47.8864, 106.9057),
    # Africa
    ("Casablanca", "Morocco", 33.5731, -7.5898),
    ("Rabat", "Morocco", 34.0209, -6.8416),
    ("Marrakesh", "Morocco", 31.6295, -7.9811),
    ("Algiers", "Algeria", 36.7538, 3.0588),
    ("Tunis", "Tunisia", 36.8065, 10.1815),
    ("Tripoli", "Libya", 32.8872, 13.1913),
    ("Khartoum", "Sudan", 15.5007, 32.5599),
    ("Addis Ababa", "Ethiopia", 9.1450, 40.4897),
    ("Nairobi", "Kenya", -1.2921, 36.8219),
    ("Mombasa", "Kenya", -4.0435, 39.6682),
    ("Kampala", "Uganda", 0.3476, 32.5825),
    ("Kigali", "Rwanda", -1.9441, 30.0619),
    ("Dar es Salaam", "Tanzania", -6.7924, 39.2083),
    ("Lagos", "Nigeria", 6.5244, 3.3792),
    ("Abuja", "Nigeria", 9.0765, 7.3986),
    ("Accra", "Ghana", 5.6037, -0.1870),
    ("Dakar", "Senegal", 14.7167, -17.4677),
    ("Abidjan", "Ivory Coast", 5.3599, -4.0083),
    ("Kinshasa", "DR Congo", -4.4419, 15.2663),
    ("Luanda", "Angola", -8.8390, 13.2894),
    ("Johannesburg", "South Africa", -26.2041, 28.0473),
    ("Cape Town", "South Africa", -33.9249, 18.4241),
    ("Durban", "South Africa", -29.8587, 31.0218),
    ("Maputo", "Mozambique", -25.9692, 32.5732),
    ("Alexandria", "Egypt", 31.2001, 29.9187),
    ("Giza", "Egypt", 30.0131, 31.2089),
    # Oceania
    ("Sydney", "Australia", -33.8688, 151.2093),
    ("Melbourne", "Australia", -37.8136, 144.9631),
    ("Brisbane", "Australia", -27.4698, 153.0251),
    ("Perth", "Australia", -31.9505, 115.8605),
    ("Adelaide", "Australia", -34.9285, 138.6007),
    ("Canberra", "Australia", -35.2809, 149.1300),
    ("Auckland", "New Zealand", -36.8509, 174.7645),
    ("Wellington", "New Zealand", -41.2866, 174.7756),
    ("Christchurch", "New Zealand", -43.5321, 172.6362),
    # Latin America
    ("Mexico City", "Mexico", 19.4326, -99.1332),
    ("Guadalajara", "Mexico", 20.6597, -103.3496),
    ("Monterrey", "Mexico", 25.6866, -100.3161),
    ("Cancún", "Mexico", 21.1619, -86.8515),
    ("Tijuana", "Mexico", 32.5149, -117.0382),
    ("Bogotá", "Colombia", 4.7110, -74.0721),
    ("Medellín", "Colombia", 6.2442, -75.5812),
    ("Lima", "Peru", -12.0464, -77.0428),
    ("Santiago", "Chile", -33.4489, -70.6693),
    ("São Paulo", "Brazil", -23.5505, -46.6333),
    ("Rio de Janeiro", "Brazil", -22.9068, -43.1729),
    ("Brasília", "Brazil", -15.8267, -47.9218),
    ("Buenos Aires", "Argentina", -34.6037, -58.3816),
    ("Caracas", "Venezuela", 10.4806, -66.9036),
    ("Quito", "Ecuador", -0.1807, -78.4678),
    ("Havana", "Cuba", 23.1136, -82.3666),
    ("San Juan", "Puerto Rico", 18.4655, -66.1057),
    ("Panama City", "Panama", 8.9824, -79.5199),
    ("San José", "Costa Rica", 9.9281, -84.0907),
    ("Montevideo", "Uruguay", -34.9011, -56.1645),
]

# Build lookup structures
CITY_INDEX = {}
for city, country, lat, lng in CITY_DB:
    key = city.lower()
    if key not in CITY_INDEX:
        CITY_INDEX[key] = {"city": city, "country": country, "lat": lat, "lng": lng}


def _load_data():
    """Load supporters from the JSON store."""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('supporters', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_data(supporters):
    """Persist supporters to the JSON store."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"supporters": supporters}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # silently fail on write


def search_cities(query):
    """
    Search the city database by partial match (case-insensitive).
    Returns a list of {city, country, lat, lng} dicts.
    """
    q = (query or '').strip().lower()
    if not q:
        return []
    results = []
    for key, entry in CITY_INDEX.items():
        if q in key or q in entry['country'].lower():
            results.append(entry)
        if len(results) >= 8:
            break
    return results


def list_supporters():
    """Return all supporters sorted newest first."""
    supporters = _load_data()
    supporters.sort(key=lambda s: s.get('time', ''), reverse=True)
    return supporters


def add_supporter(name, city, country, lat, lng, vibe, note=None):
    """Add a new supporter to the store."""
    supporters = _load_data()
    supporter = {
        "id": uuid.uuid4().hex[:12],
        "name": (name or '').strip()[:40],
        "city": (city or '').strip()[:60],
        "country": (country or '').strip()[:60],
        "lat": lat,
        "lng": lng,
        "vibe": vibe if vibe in VIBES else "Global Grid",
        "note": (note or '').strip()[:80],
        "time": time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
    }
    supporters.append(supporter)
    _save_data(supporters)
    return supporter


# ─── Flask-friendly handlers (used by web_app.py) ───
def handle_get():
    """GET /api/supporters → list all supporters."""
    return list_supporters()


def handle_add(payload):
    """POST /api/supporters → add a supporter."""
    name = payload.get('name', '')
    city = payload.get('city', '')
    country = payload.get('country', '')
    lat = payload.get('lat')
    lng = payload.get('lng')
    vibe = payload.get('vibe', 'Global Grid')
    note = payload.get('note', '')

    if not city:
        return {"error": "City is required"}, 400

    # If lat/lng missing, try to resolve from city database
    if lat is None or lng is None:
        match = CITY_INDEX.get(city.strip().lower())
        if match:
            lat, lng = match['lat'], match['lng']
        else:
            return {"error": "Please select a city from the suggestions"}, 400

    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        return {"error": "Invalid coordinates"}, 400

    supporter = add_supporter(name, city, country, lat, lng, vibe, note)
    return supporter, 201