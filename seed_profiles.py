# ---------- Test profile seeding (realistic availability) ----------
from app import save_profile, PASSWORDS_FILE,PROFILES_DIR, list_pr
from datetime import datetime, timedelta, timezone
import random

FIRST_NAMES = [
    "Olivia", "Noah", "Amelia", "Jack", "Isla", "Leo", "Mia", "Henry",
    "Ava", "Hudson", "Zara", "Ethan", "Chloe", "Liam", "Sophie", "Lucas",
    "Archie", "Emily", "Harper", "Aria", "Thea", "Elijah", "Aiden", "Grace",
    "Ruby", "Oliver", "Charlotte", "William", "Ivy", "Mason", "Hannah"
]

LAST_NAMES = [
    "Nguyen", "Smith", "Williams", "Brown", "Jones", "Taylor", "Wilson",
    "Martin", "Thompson", "White", "Walker", "Hall", "Young", "King",
    "Wright", "Scott", "Green", "Baker", "Adams", "Mitchell", "Campbell",
    "Stewart", "Morris", "Carter", "Roberts", "Cooper", "Phillips", "Turner"
]

CORE_CLASSES = ["INFO1111", "MATH1001", "STAT2011", "INFO1911", "COMP2123", "DATA1001"]

def _random_username(first, last, used):
    # e.g., Olivia Nguyen -> ongu01; guarantee uniqueness
    base = (first[0] + last).lower()
    for i in range(1, 1000):
        candidate = f"{base}{i:02d}"
        if candidate not in used:
            return candidate
    # fallback
    candidate = base + str(random.randint(1000, 9999))
    while candidate in used:
        candidate = base + str(random.randint(1000, 9999))
    return candidate

def _random_classes():
    # 3–4 classes per student
    k = random.choice([3, 3, 4])
    return sorted(random.sample(CORE_CLASSES, k))

def _random_day_slots():
    """
    Build realistic, non-overlapping availability blocks for Mon–Fri
    within typical study times (09:00–17:00).
    Strategy:
      - 4–5 days available
      - For each chosen day, 3-5 blocks of 60–120 minutes
      - Start times aligned to :00 or :30
    """
    days = ["Mon","Tue","Wed","Thu","Fri"]
    chosen_days = random.sample(days, random.choice([4, 5]))
    blocks = []
    for d in chosen_days:
        num_blocks = random.choice([3, 4, 5])
        taken = []
        for _ in range(num_blocks):
            start_hour = random.randint(9, 16)     # latest start 16:00 for a 60-min block
            start_min  = random.choice([0, 30])
            dur_min    = random.choice([60, 90, 120])
            sh, sm = start_hour, start_min
            eh = sh + (sm + dur_min)//60
            em = (sm + dur_min) % 60
            # clamp to 17:00
            end_ok_h = min(eh, 17)
            end_ok_m = em if eh <= 17 else 0
            # Simple overlap check with existing blocks that day
            # Represent times as minutes since 00:00 for the day
            s_total = sh*60 + sm
            e_total = end_ok_h*60 + end_ok_m
            if e_total - s_total < 60:
                continue  # keep min 60 min
            clash = False
            for (s2, e2) in taken:
                if not (e_total <= s2 or s_total >= e2):
                    clash = True; break
            if clash:
                continue
            taken.append((s_total, e_total))
            blocks.append({
                "day": d,
                "start": f"{sh:02d}:{sm:02d}",
                "end":   f"{end_ok_h:02d}:{end_ok_m:02d}"
            })
    # Sort for nice display
    day_index = {d:i for i,d in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])}
    blocks.sort(key=lambda b: (day_index[b["day"]], b["start"]))
    return blocks

def _save_plaintext_password(username, password):
    with open(PASSWORDS_FILE, "a", encoding="utf-8") as fh:
        fh.write(f"{username}:{password}\n")

def seed_profiles(count=50):
    """
    Create 'count' new student profiles, with realistic availability and classes.
    Existing usernames are not overwritten; we skip if file already exists.
    Password for each new account: <username>123
    """
    used = {p["username"] for p in list_pr()}  # current usernames
    created = 0
    attempts = 0
    while created < count and attempts < count*5:
        attempts += 1
        first = random.choice(FIRST_NAMES)
        last  = random.choice(LAST_NAMES)
        username = _random_username(first, last, used)
        if (PROFILES_DIR / f"{username}.json").exists():
            continue
        classes = _random_classes()
        availability = _random_day_slots()
        profile = {
            "username": username,
            "name": f"{first} {last}",
            "classes": classes,
            "availability": availability,
            "dob": f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{random.randint(1990, 2010)}",
            "address": f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Elm', 'Maple', 'Pine', 'Holt', 'Dingo', 'Kookaburra'])} {random.choice(['St', 'Rd', 'Ln'])}, Sydney NSW {random.randint(2000, 2999)}",
            "created_at": datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=11))).strftime('%H:%M - %d/%m/%Y'),
            "last_login": None
        }
        save_profile(profile)
        _save_plaintext_password(username, f"{username}123")
        used.add(username)
        created += 1
    return created


def cli_seed_profiles(n=50):
    print("Seeding profiles...")
    created = seed_profiles(n)
    print(f"Created {created} new profiles.")
