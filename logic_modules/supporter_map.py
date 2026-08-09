"""
Supporter Map backend for the Global Supporter Map page.
Provides:
  - Persistent JSON storage of supporter pins
  - Type-ahead city/country database with approximate lat/lng
  - Vibe badge definitions
  - API handler functions for GET (list) and POST (add)
"""
import json
import os
import uuid
import time

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'supporters_data.json')

# ─── Vibe Badges ───
VIBES = {
    "Local Rooted": {"emoji": "🌱", "color": "#2e7d32"},
    "Racing Fan Zone": {"emoji": "🏁", "color": "#d21214"},
    "Tech Hub": {"emoji": "💻", "color": "#406bbf"},
    "Globe Trotter": {"emoji": "🌍", "color": "#e68a00"}
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
    # Canada
    ("Toronto", "Canada", 43.6532, -79.3832),
    ("Vancouver", "Canada", 49.2827, -123.1207),
    ("Montreal", "Canada", 45.5017, -73.5673),
    ("Ottawa", "Canada", 45.4215, -75.6972),
    ("Calgary", "Canada", 51.0447, -114.0719),
    ("Edmonton", "Canada", 53.5461, -113.4938),
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
    # Middle East
    ("Dubai", "UAE", 25.2048, 55.2708),
    ("Abu Dhabi", "UAE", 24.4539, 54.3773),
    ("Riyadh", "Saudi Arabia", 24.7136, 46.6753),
    ("Jeddah", "Saudi Arabia", 21.4858, 39.1925),
    ("Mecca", "Saudi Arabia", 21.3891, 39.8579),
    ("Medina", "Saudi Arabia", 24.5247, 39.5692),
    ("Istanbul", "Turkey", 41.0082, 28.9784),
    ("Ankara", "Turkey", 39.9334, 32.8597),
    ("Tehran", "Iran", 35.6892, 51.3890),
    ("Baghdad", "Iraq", 33.3152, 44.3661),
    ("Basra", "Iraq", 30.5081, 47.7805),
    ("Erbil", "Iraq", 36.1911, 44.0092),
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
    # South & Central Asia
    ("Karachi", "Pakistan", 24.8607, 67.0011),
    ("Lahore", "Pakistan", 31.5204, 74.3587),
    ("Islamabad", "Pakistan", 33.6844, 73.0479),
    ("Mumbai", "India", 19.0760, 72.8777),
    ("New Delhi", "India", 28.6139, 77.2090),
    ("Kolkata", "India", 22.5726, 88.3639),
    ("Chennai", "India", 13.0827, 80.2707),
    ("Hyderabad", "India", 17.3850, 78.4867),
    ("Dhaka", "Bangladesh", 23.8103, 90.4125),
    ("Kabul", "Afghanistan", 34.5553, 69.2075),
    ("Tashkent", "Uzbekistan", 41.2995, 69.2401),
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
    ("Seoul", "South Korea", 37.5665, 126.9780),
    ("Beijing", "China", 39.9042, 116.4074),
    ("Shanghai", "China", 31.2304, 121.4737),
    ("Hong Kong", "China", 22.3193, 114.1694),
    ("Taipei", "Taiwan", 25.0330, 121.5654),
    ("Singapore", "Singapore", 1.3521, 103.8198),
    ("Kuala Lumpur", "Malaysia", 3.1390, 101.6869),
    ("Jakarta", "Indonesia", -6.2088, 106.8456),
    ("Bangkok", "Thailand", 13.7563, 100.5018),
    ("Manila", "Philippines", 14.5995, 120.9842),
    ("Ho Chi Minh City", "Vietnam", 10.8231, 106.6297),
    ("Hanoi", "Vietnam", 21.0278, 105.8342),
    ("Phnom Penh", "Cambodia", 11.5564, 104.9282),
    ("Yangon", "Myanmar", 16.8409, 96.1735),
    ("Kathmandu", "Nepal", 27.7172, 85.3240),
    ("Colombo", "Sri Lanka", 6.9271, 79.8612),
    ("Ulaanbaatar", "Mongolia", 47.8864, 106.9057),
    # Africa
    ("Cairo", "Egypt", 30.0444, 31.2357),
    ("Casablanca", "Morocco", 33.5731, -7.5898),
    ("Rabat", "Morocco", 34.0209, -6.8416),
    ("Algiers", "Algeria", 36.7538, 3.0588),
    ("Tunis", "Tunisia", 36.8065, 10.1815),
    ("Tripoli", "Libya", 32.8872, 13.1913),
    ("Khartoum", "Sudan", 15.5007, 32.5599),
    ("Addis Ababa", "Ethiopia", 9.1450, 40.4897),
    ("Nairobi", "Kenya", -1.2921, 36.8219),
    ("Kampala", "Uganda", 0.3476, 32.5825),
    ("Kigali", "Rwanda", -1.9441, 30.0619),
    ("Dar es Salaam", "Tanzania", -6.7924, 39.2083),
    ("Lagos", "Nigeria", 6.5244, 3.3792),
    ("Accra", "Ghana", 5.6037, -0.1870),
    ("Dakar", "Senegal", 14.7167, -17.4677),
    ("Abidjan", "Ivory Coast", 5.3599, -4.0083),
    ("Kinshasa", "DR Congo", -4.4419, 15.2663),
    ("Luanda", "Angola", -8.8390, 13.2894),
    ("Johannesburg", "South Africa", -26.2041, 28.0473),
    ("Cape Town", "South Africa", -33.9249, 18.4241),
    ("Maputo", "Mozambique", -25.9692, 32.5732),
    # Oceania
    ("Sydney", "Australia", -33.8688, 151.2093),
    ("Melbourne", "Australia", -37.8136, 144.9631),
    ("Brisbane", "Australia", -27.4698, 153.0251),
    ("Perth", "Australia", -31.9505, 115.8605),
    ("Auckland", "New Zealand", -36.8509, 174.7645),
    ("Wellington", "New Zealand", -41.2866, 174.7756),
    # Latin America
    ("Mexico City", "Mexico", 19.4326, -99.1332),
    ("Guadalajara", "Mexico", 20.6597, -103.3496),
    ("Monterrey", "Mexico", 25.6866, -100.3161),
    ("Cancún", "Mexico", 21.1619, -86.8515),
    ("Bogotá", "Colombia", 4.7110, -74.0721),
    ("Lima", "Peru", -12.0464, -77.0428),
    ("Santiago", "Chile", -33.4489, -70.6693),
    ("São Paulo", "Brazil", -23.5505, -46.6333),
    ("Rio de Janeiro", "Brazil", -22.9068, -43.1729),
    ("Buenos Aires", "Argentina", -34.6037, -58.3816),
    ("Caracas", "Venezuela", 10.4806, -66.9036),
    ("Quito", "Ecuador", -0.1807, -78.4678),
    ("Havana", "Cuba", 23.1136, -82.3666),
    ("San Juan", "Puerto Rico", 18.4655, -66.1057),
    ("Panama City", "Panama", 8.9824, -79.5199),
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
        "vibe": vibe if vibe in VIBES else "Globe Trotter",
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
    vibe = payload.get('vibe', 'Globe Trotter')
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