
from flask import Flask, render_template, request, redirect, url_for, session, abort
import os, json, csv
from pathlib import Path
from datetime import datetime, timedelta, timezone
from functools import wraps
from time import perf_counter
import uuid
from werkzeug.security import check_password_hash, generate_password_hash

# where the app stores data files (profiles, passwords, bookings, notifications, rooms)
APP_ROOT = Path(__file__).parent
DATA_DIR = APP_ROOT / 'data'
PROFILES_DIR = DATA_DIR / 'profiles'
PASSWORDS_FILE = DATA_DIR / 'passwords.txt'
BOOKINGS_FILE = DATA_DIR / 'bookings.jsonl'
NOTES_FILE = DATA_DIR / 'notifications.jsonl'
PASSWORD_RESET_REQUESTS_FILE = DATA_DIR / 'password_reset_requests.jsonl'
ROOMS_CSV = DATA_DIR / 'rooms.csv'

APP_MODE = os.getenv('APP_MODE', 'local')
ENABLE_DIAG = os.getenv('ENABLE_DIAG', 'true').lower() == 'true'
SEED_ON_START = os.getenv('SEED_ON_START', 'false').lower() == 'true'

# create the app
app = Flask(__name__)
app.secret_key = 'dev-secret-key' 

# --------------- Helpers ---------------

def load_profile(username):
    f = PROFILES_DIR / f"{username}.json"
    if not f.exists(): # user profile data doesn't exist
        return None
    try:
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read().strip()
            if not content: # malformed profile
                return None
            return json.loads(content) # successfully loaded profile
    except Exception:
        return None # any error (IO, JSON parsing, etc) treated as missing profile

# TODO: fix thing
def save_profile(profile):
    f = PROFILES_DIR / f"{profile['username']}.json"
    with open(f, 'w', encoding='utf-8') as fh:
        json.dump(profile, fh, indent=2)


def list_pr():
    pr = []
    for p in sorted(PROFILES_DIR.glob('*.json')):
        try:
            with open(p, 'r', encoding='utf-8') as fh:
                pr.append(json.load(fh))
        except Exception as e:
            pass
    return pr


def passwords_map():
    m = {}
    if PASSWORDS_FILE.exists():
        with open(PASSWORDS_FILE, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                if ':' in line:
                    u, pw = line.split(':', 1)
                    m[u] = pw
    return m


def set_pwd(username, password):
    with open(PASSWORDS_FILE, 'a', encoding='utf-8') as fh:
        fh.write(f"{username}:{generate_password_hash(password)}\n")


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped





def Append_Jsonl(path: Path, obj):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(obj) + '\n')







def readjsonl(path: Path):
    rows = []
    if not path.exists():
        return rows
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows

def get_user_notifications(username):
    """Return (notes, unread_count) for a user. Missing 'read' -> treat as False (unread)."""
    notes = []
    unread = 0
    for n in readjsonl(NOTES_FILE):
        if n.get('to') == username:
            if 'read' not in n:
                n['read'] = False
            if not n.get('id'):
                n['id'] = f"{n.get('to','')}|{n.get('created_at','')}|{hash(n.get('message','')) & 0xffffffff}"
            notes.append(n)
            if not n['read']:
                unread += 1
    # Sort newest first
    notes.sort(key=lambda x: x.get('created_at',''), reverse=True)
    return notes, unread


def set_notification_read(username, note_id, read=True):
    """Mark a single notification (by id) as read/unread for the given user."""
    rows = readjsonl(NOTES_FILE)
    changed = False
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        for n in rows:
            if n.get('to') == username:
                if 'read' not in n:
                    n['read'] = False
                if not n.get('id'):
                    n['id'] = f"{n.get('to','')}|{n.get('created_at','')}|{hash(n.get('message','')) & 0xffffffff}"
                if n.get('id') == note_id:
                    n['read'] = bool(read)
                    changed = True
            f.write(json.dumps(n) + '\n')
    return changed


def set_all_notifications_read(username, read=True):
    """Mark all notifications for the user as read/unread."""
    rows = readjsonl(NOTES_FILE)
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        for n in rows:
            if n.get('to') == username:
                if 'read' not in n:
                    n['read'] = False
                n['read'] = bool(read)
            f.write(json.dumps(n) + '\n')

def loadRooms():
    rooms = []
    
    if ROOMS_CSV.exists():
        
        
        with open(ROOMS_CSV, 'r', encoding='utf-8') as f:
            for i, row in enumerate(csv.reader(f)):
                
                
                
                if i == 0:
                    
                    
                    continue
                
                if row:
                    
                    
                    rooms.append(row[0])
    return rooms

# Availability utilities
DAYS = ['Mon','Tue','Wed','Thu','Fri']

def parse_availability_slots(av_list):
    slots = set()
    for a in av_list or []:
        day, start, end = a.get('day'), a.get('start'), a.get('end')
        try:
            if day not in DAYS:
                continue
            sh, sm = [int(x) for x in start.split(':')]; eh, em = [int(x) for x in end.split(':')]
            t = datetime(2000,1,3,sh,sm); stop = datetime(2000,1,3,eh,em)
            while t < stop:
                slots.add((day, f"{t.hour:02d}:{t.minute:02d}"))
                t += timedelta(minutes=30)
        except Exception:
            pass
    return slots


def intersectSlots(usernames):
    common = None
    for u in usernames:
        
        p = load_profile(u)
        if not p:
            
            
            continue
        
        s = parse_availability_slots(p.get('availability', []))
        if common is None:
            
            common = s
        else:
            
            
            common = common.intersection(s)
    return common or set()


def _add_30(hhmm):
    h, m = [int(x) for x in hhmm.split(':')]
    dt = datetime(2000,1,3,h,m) + timedelta(minutes=30)
    return f"{dt.hour:02d}:{dt.minute:02d}"


def slots_2_blocks(slots):
    by_day = {}
    for day, hhmm in slots:
        by_day.setdefault(day, []).append(hhmm)
    results = []
    for day, times in by_day.items():
        times_sorted = sorted(times)
        if not times_sorted:
            continue
        start = times_sorted[0]
        prev = start
        for t in times_sorted[1:]:
            ph, pm = [int(x) for x in prev.split(':')]; th, tm = [int(x) for x in t.split(':')]
            prev_dt = datetime(2000,1,3,ph,pm); this_dt = datetime(2000,1,3,th,tm)
            if (this_dt - prev_dt).total_seconds() == 1800:
                prev = t
            else:
                results.append({'day': day, 'start': start, 'end': _add_30(prev)})
                start = t
                prev = t
        results.append({'day': day, 'start': start, 'end': _add_30(prev)})
    filtered = []
    for b in results:
        sh, sm = [int(x) for x in b['start'].split(':')]
        eh, em = [int(x) for x in b['end'].split(':')]
        if (eh*60+em) - (sh*60+sm) >= 60:
            filtered.append(b)
    return sorted(filtered, key=lambda x: (DAYS.index(x['day']), x['start']))

def block_start_end_options(block):
    """Return (start_options, end_options) at 30-min increments inside the block."""
    sh, sm = [int(x) for x in block['start'].split(':')]
    
    
    
    eh, em = [int(x) for x in block['end'].split(':')]
    t0 = datetime(2000, 1, 3, sh, sm); stop = datetime(2000, 1, 3, eh, em)


    # all possible 30-min STARTS (inclusive of start, exclusive of stop)
    st = []
    
    
    t = t0
    
    while t < stop:
        st.append(t.strftime('%H:%M'))
        t += timedelta(minutes=30)


    # all possible 30-min ENDS (strictly after start; inclusive of stop)
    es = []
    
    t = t0 + timedelta(minutes=30)
    
    while t <= stop:
        es.append(t.strftime('%H:%M'))
        t += timedelta(minutes=30)

    return st, es

def conflicts(b, day, start, end):
    if b.get('day') != day:
        return False
    s1 = b.get('start'); e1 = b.get('end')
    return not (end <= s1 or start >= e1)


# --------------- Routes ---------------

@app.route('/')
def home():
    return render_template('home.html')

# Auth
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', ''); password = request.form.get('password', ''); pw_map = passwords_map()
        if username in pw_map and check_password_hash(pw_map[username], password):
            session['username'] = username
            prof = load_profile(username)
            if prof:
                prof['last_login'] = datetime.utcnow().isoformat() + 'Z'
                save_profile(prof)
            return redirect(url_for('home'))
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    message = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        Append_Jsonl(PASSWORD_RESET_REQUESTS_FILE, {
            'username': username,
            'requested_at': datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=11))).strftime('%H:%M -%d/%m/%Y')
        })
        message = 'If this account exists, a password reset request has been recorded.'
    return render_template('forgot.html', message=message)

# Signup/Profile
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        name = request.form.get('name', ''); username = request.form.get('username', ''); password = request.form.get('password', '')
        classes_str = request.form.get('classes', '')
        dob = request.form.get('dob', '')
        address = request.form.get('address', '')
        availability_text = request.form.get('availability', '')
        if not username:
            error = 'Username required'
        else:
            classes = [c.strip() for c in classes_str.split(',') if c.strip()]
            availability = []
            for line in availability_text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    day, times = line.split(' ', 1)
                    start, end = times.split('-', 1)
                    availability.append({'day': day, 'start': start.strip(), 'end': end.strip()})
                except Exception:
                    pass
            profile = {
                'username': username,
                'name': name,
                'classes': classes,
                'availability': availability,
                'dob': dob,
                'address': address,
                'created_at': datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=11))).strftime('%H:%M -%d/%m/%Y'),
                'last_login': None
            }
            save_profile(profile)
            set_pwd(username, password)
            session['username'] = username
            return redirect(url_for('profile'))
    return render_template('signup.html', error=error)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = session.get('username')
    prof = load_profile(username)
    if request.method == 'POST':
        name = request.form.get('name', prof.get('name', ''))
        classes_str = request.form.get('classes', ','.join(prof.get('classes', [])))
        dob = request.form.get('dob', prof.get('dob', ''))
        address = request.form.get('address', prof.get('address', ''))
        availability_text = request.form.get('availability', '')
        classes = [c.strip() for c in classes_str.split(',') if c.strip()]
        availability = []
        for line in availability_text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                day, times = line.split(' ', 1)
                start, end = times.split('-', 1)
                availability.append({'day': day, 'start': start.strip(), 'end': end.strip()})
            except Exception:
                pass
        prof.update({'name': name,'classes': classes,'dob': dob,'address': address,'availability': availability})
        save_profile(prof)
    prof = load_profile(username)
    user_vm = {
        'name': prof.get('name', ''),
        'classes': ','.join(prof.get('classes', [])),
        'dob': prof.get('dob', ''),
        'address': prof.get('address', ''),
        'availability_text': '\n'.join([f"{a['day']} {a['start']}-{a['end']}" for a in prof.get('availability', [])])}
    return render_template('profile.html', user=user_vm)
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profEdit(username):
    if session.get('username') != username:
        abort(403)

    # Load or create a minimal profile if missing
    prof = load_profile(username) or {
        'username': username, 'name': '', 'classes': [], 'availability': [],
        'dob': '', 'address': '', 'created_at': datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=11))).strftime('%H:%M -%d/%m/%Y'),
        'last_login': None
    }

    if request.method == 'POST':
        name = request.form.get('name', prof.get('name', ''))
        classes_str = request.form.get('classes', ','.join(prof.get('classes', [])))
        dob = request.form.get('dob', prof.get('dob', ''))
        address = request.form.get('address', prof.get('address', ''))
        availability_text = request.form.get('availability', '')
        classes = [c.strip() for c in classes_str.split(',') if c.strip()]
        availability = []
        for line in availability_text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                day, times = line.split(' ', 1)
                start, end = times.split('-', 1)
                availability.append({'day': day, 'start': start.strip(), 'end': end.strip()})
            except Exception:
                pass
        prof.update({
            'name': name, 'classes': classes, 'dob': dob,
            'address': address, 'availability': availability
        })
        save_profile(prof)

    # Rebuild VM for template (reuse the same form/template as your own profile)
    prof = load_profile(username)
    user_vm = {
        'name': prof.get('name', ''),
        'classes': ','.join(prof.get('classes', [])),
        'dob': prof.get('dob', ''),
        'address': prof.get('address', ''),
        'availability_text': '\n'.join([f"{a['day']} {a['start']}-{a['end']}" for a in prof.get('availability', [])])
    }
    return render_template('profile.html', user=user_vm)
# Profiles
@app.route('/profiles')
@login_required
def profiles():
    profiles = list_pr()
    return render_template('profiles.html', profiles=profiles)

@app.route('/profiles/search')
@login_required
def profile_search():
    query = request.args.get('query', '')
    fmt = request.args.get('format', '').lower()
    results = []
    if query:
        for p in list_pr():
            # exact, case-sensitive matches only (intentionally)
            if p.get('username') == query or p.get('name') == query or (query in p.get('classes', [])):
                results.append(p)
    if fmt == 'json':
        # Compact payload for the live search dropdown
        compact = [
            {
                'username': p.get('username'),
                'name': p.get('name'),
                'classes': p.get('classes', []),
            }
            for p in results[:10]
        ]
        from flask import jsonify as do_me_a_flasky_thing
        return do_me_a_flasky_thing({'results': compact})
    return render_template('profiles.html', profiles=results)

# Bookings (M2)
@app.route('/bookings')
@login_required
def my_bookings():
    username = session.get('username')
    bs = []
    for b in readjsonl(BOOKINGS_FILE):
        if username and username == b.get('created_by'):
            bs.append(b)
    return render_template('bookings.html', bookings=bs)

@app.route('/bookings/new')
@login_required
def booking_start():
    session.pop('booking_draft', None)
    return render_template('booking_start.html')

@app.route('/bookings/new/class', methods=['POST'])
@login_required
def booking_choose_class():
    class_name = request.form.get('class_name','')
    session['booking_draft'] = {'class_name': class_name, 'people': [], 'slot': None}
    candidates = []
    for p in list_pr():
        if class_name in (p.get('classes') or []):
            candidates.append(p)
    return render_template('booking_people.html', class_name=class_name, candidates=candidates)

@app.route('/bookings/new/people', methods=['POST'])
@login_required
def booking_choose_people():
    draft = session.get('booking_draft', {})
    people = request.form.getlist('people')
    draft['people'] = people
    session['booking_draft'] = draft
    participants = list(people)
    if session.get('username'):
        if session['username'] not in participants:
            participants.append(session['username'])
    
    # compute mutual availability as BLOCKS, then build start/end options per block
    common = intersectSlots(participants)      # set of (day, 'HH:MM')
    blocks = slots_2_blocks(common)            # [{'day','start','end'}, ...] sorted

    # enrich each block with 30-min start/end options
    for b in blocks:
        starts, ends = block_start_end_options(b)
        b['start_options'] = starts
        b['end_options'] = ends

    return render_template('booking_time.html', blocks=blocks)

@app.route('/bookings/new/time', methods=['POST'])
@login_required
def booking_choose_time():
    draft = session.get('booking_draft', {})
    
    slot_day = request.form.get('day')
    slot_start = request.form.get('start')
    slot_end = request.form.get('end')

    if not (slot_day and slot_start and slot_end):
        return redirect(url_for('booking_start'))

    # Load draft and derive participants (same logic you used in /bookings/new/people)
    draft = session.get('booking_draft', {})
    people = draft.get('people', [])
    participants = list(people)
    if session.get('username') and session['username'] not in participants:
        participants.append(session['username'])

    # Validate: start < end and every 30-min subslot is mutually available
    try:
        sh, sm = [int(x) for x in slot_start.split(':')]
        eh, em = [int(x) for x in slot_end.split(':')]
    except Exception as e:
        return redirect(url_for('booking_start'))

    start_dt = datetime(2000, 1, 3, sh, sm)
    end_dt   = datetime(2000, 1, 3, eh, em)
    if not (start_dt < end_dt):
        # invalid range
        # (optionally: re-render with an error message)
        return redirect(url_for('booking_start'))

    # Build the mutual set again for validation
    common = intersectSlots(participants)  # set of (day, 'HH:MM')

    # Walk 30-min steps from start to (exclusive) end and ensure each subslot is mutual
    t = start_dt
    valid = True
    while t < end_dt:
        hhmm = t.strftime('%H:%M') # parse to date-time
        if (slot_day, hhmm) not in common: # check mutual availability
            valid = False # no mutual availability for this subslot
            break
        t += timedelta(minutes=30) # step to next subslot

    if not valid:
        # Out of mutual range; back to start (or re-render with message)
        return redirect(url_for('booking_start'))

    # All good: store the chosen range
    draft['slot'] = {'day': slot_day, 'start': slot_start, 'end': slot_end}
    session['booking_draft'] = draft

    # proceed to rooms as before (unchanged code below)
    rooms = loadRooms()
    avail = []
    existing = readjsonl(BOOKINGS_FILE)
    for r in rooms:
        clash = False
        for b in existing:
            if b.get('room') == r and conflicts(b, slot_day, slot_start, slot_end):
                clash = True
                break
        if not clash:
            avail.append(r)
    return render_template('booking_room.html', rooms=avail)

@app.route('/bookings/new/room', methods=['POST'])
@login_required
def booking_choose_room():
    draft = session.get('booking_draft', {})
    room = request.form.get('room')
    if not room or 'slot' not in draft:
        return redirect(url_for('booking_start'))
    class_name = draft.get('class_name','')
    people = draft.get('people', [])
    creator = session.get('username')
    participants = list(people)
    if creator and creator not in participants:
        participants.append(creator)
    booking = {
        'class_name': class_name,
        'participants': participants,
        'day': draft['slot']['day'],
        'start': draft['slot']['start'],
        'end': draft['slot']['end'],
        'room': room,
        'created_at': datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=11))).strftime('%H:%M -%d/%m/%Y'),
        'created_by': creator or 'anonymous'
        }
    Append_Jsonl(BOOKINGS_FILE, booking)
    for u in participants:
        msg = f"You have a new {class_name} meeting on {booking['day']} {booking['start']}-{booking['end']} in {room}."
        Append_Jsonl(NOTES_FILE, {
            'id': str(uuid.uuid4()),
            'to': u,
            'message': msg,
            'created_at': datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=11))).strftime('%H:%M -%d/%m/%Y'),
            'read': False
        })
    session.pop('booking_draft', None)
    return redirect(url_for('my_bookings'))

# Notifications
@app.route('/inbox')
@login_required
def inbox():
    username = session.get('username')
    notes, unread = get_user_notifications(username)
    return render_template('inbox.html', notes=notes, unread=unread)
@app.route('/inbox/read', methods=['POST'])
@login_required
def inbox_mark_read():
    username = session.get('username')
    note_id = request.form.get('id', '')
    action = request.form.get('action', 'read')  # 'read' or 'unread'
    set_notification_read(username, note_id, read=(action == 'read'))
    return redirect(url_for('inbox'))
@app.route('/inbox/read-all', methods=['POST'])
@login_required
def inbox_mark_all_read():
    username = session.get('username')
    set_all_notifications_read(username, read=True)
    return redirect(url_for('inbox'))
# M3: Availability visualisation (non-persistent overlay)
@app.route('/availability')
@login_required
def availability():
    username = session.get('username')
    prof = load_profile(username)
    a_slots = parse_availability_slots(prof.get('availability', [])) if prof else set()
    b_slots = set()
    for b in readjsonl(BOOKINGS_FILE):
        if username in (b.get('created_by') or []):
            day = b.get('day'); start=b.get('start'); end=b.get('end')
            try:
                sh, sm = [int(x) for x in start.split(':')]
                eh, em = [int(x) for x in end.split(':')]
                t = datetime(2000,1,3,sh,sm)
                stop = datetime(2000,1,3,eh,em)
                while t < stop:
                    b_slots.add((day, f"{t.hour:02d}:{t.minute:02d}"))
                    t += timedelta(minutes=30)
            except Exception:
                pass
    days = ['Mon','Tue','Wed','Thu','Fri']
    times = ['09:00','09:30','10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30','14:00','14:30','15:00','15:30','16:00','16:30','17:00']
    grid = []
    for d in days:
        cells = []
        for t in times:
            label = ''
            if (d, t) in a_slots:
                label = 'A'
            if (d, t) in b_slots:
                label = 'B' 
            cells.append(label)
        grid.append({'day': d, 'cells': cells})
    vm = {'username': username, 'grid': grid}
    return render_template('availability.html', vm=vm)

# M3 Diagnostics (gated)
@app.route('/diag/timing')
def DiagTiming():
    if not ENABLE_DIAG:
        abort(404)
    op = request.args.get('op', 'search')
    t0 = perf_counter()
    if op == 'search':
        _ = list_pr()
    elif op == 'intersect':
        ps = [p.get('username') for p in list_pr()][:3]
        _ = intersectSlots(ps)
    elif op == 'rooms':
        _ = loadRooms()
    dt = perf_counter() - t0
    payload = { 'op': op, 'elapsed_sec': round(dt, 6) }
    Append_Jsonl(DATA_DIR / 'diag.log.jsonl', {**payload, 'ts': datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=11))).strftime('%H:%M -%d/%m/%Y')})
    from flask import jsonify as do_me_a_flasky_thing
    return do_me_a_flasky_thing(payload)

@app.route('/diag/dumps')
def diag_dumps():
    if not ENABLE_DIAG:
        abort(404)
    sample = {
        'profile_count': len(list_pr()),
        'room_count': len(loadRooms()),
        'booking_count': len(readjsonl(BOOKINGS_FILE))
    }
    from flask import jsonify as do_me_another_flasky_thing
    return do_me_another_flasky_thing(sample)

@app.context_processor
def inject_unread_count():
    username = session.get('username')
    if not username:
        return {'unread_count': 0}
    _, unread = get_user_notifications(username)
    return {'unread_count': unread}

if __name__ == '__main__':
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not BOOKINGS_FILE.exists():
        BOOKINGS_FILE.write_text('')
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text('')
  
    # To run on a specific server you can change the host and port here
    # Currently set up for localhost and to use the flask server rather than
    # any other server method
    host = "0.0.0.0"
    port = 8000
    app.run(host=host, port=port, debug=True)
