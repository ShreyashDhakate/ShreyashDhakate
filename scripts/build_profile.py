#!/usr/bin/env python3
"""Generate self-contained SVG profile art. Daily runs use only Python stdlib."""
import argparse
import calendar
import json
import re
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BG, BORDER, TEXT, MUTED, ACCENT = '#0d1117', '#30363d', '#e6edf3', '#8b949e', '#7ee787'
PALETTE = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']


class ContributionParser(HTMLParser):
    """Join GitHub day cells to their tooltip counts by element ID."""
    def __init__(self):
        super().__init__()
        self.cells, self.tips = {}, {}
        self.tip_id, self.parts = None, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-date' in attrs and 'data-level' in attrs:
            self.cells[attrs['id']] = {
                'date': attrs['data-date'], 'level': int(attrs['data-level']),
                'inline_count': attrs.get('data-count')
            }
        if tag == 'tool-tip':
            self.tip_id, self.parts = attrs.get('for'), []

    def handle_data(self, data):
        if self.tip_id is not None:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tip_id is not None:
            self.tips[self.tip_id] = ''.join(self.parts).strip()
            self.tip_id = None

    def days(self):
        result = []
        for element_id, cell in self.cells.items():
            label = self.tips.get(element_id, '')
            match = re.match(r'([\d,]+) contributions?\b', label, re.I)
            if cell['inline_count'] is not None:
                count = int(cell['inline_count'])
            elif match:
                count = int(match.group(1).replace(',', ''))
            elif re.match(r'No contributions?\b', label, re.I):
                count = 0
            else:
                raise ValueError(f'Missing count for {cell["date"]}; keeping the previous graph.')
            day = date.fromisoformat(cell['date'])
            if not 0 <= cell['level'] <= 4 or count < 0:
                raise ValueError('Invalid contribution level/count.')
            result.append({'date': day.isoformat(), 'count': count, 'level': cell['level']})
        result.sort(key=lambda item: item['date'])
        if len(result) < 350 or len({d['date'] for d in result}) != len(result):
            raise ValueError('Contribution calendar is incomplete; keeping the previous graph.')
        for previous, current in zip(result, result[1:]):
            if date.fromisoformat(current['date']) - date.fromisoformat(previous['date']) != timedelta(days=1):
                raise ValueError('Calendar contains missing days.')
        return result


def svg_start(width, height, title, description):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
        '<style>text{font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace} @media(prefers-reduced-motion:reduce){animate,animateTransform{display:none}}</style>',
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="{BG}" stroke="{BORDER}"/>',
        '<circle cx="19" cy="20" r="4" fill="#f85149"/><circle cx="33" cy="20" r="4" fill="#d29922"/><circle cx="47" cy="20" r="4" fill="#3fb950"/>',
    ]


def text(x, y, content, color=TEXT, size=12, extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" {extra}>{escape(str(content))}</text>'


def reveal(begin, duration=.35):
    return f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.3f}s" dur="{duration}s" fill="freeze"/>'


def save_svg(path, parts):
    path.write_text('\n'.join(parts + ['</svg>']) + '\n', encoding='utf-8')


def render_info(profile):
    parts = svg_start(540, 370, 'About Shreyash Dhakate', 'Backend developer, IIT Kharagpur, experience, technology stack and competitive programming.')
    parts += [text(65, 24, 'shreyash@github: ~', MUTED, 11), text(24, 61, profile['name'], ACCENT, 21)]
    parts += [text(24, 85, 'building the services behind the product', MUTED, 12)]
    parts += [f'<path d="M24 102 H516" stroke="{BORDER}"/>']
    for i, (key, value) in enumerate(profile['rows']):
        y = 126 + i * 22
        parts += [f'<g>{reveal(.25+i*.12)}', text(24, y, key, '#79c0ff', 11.5), text(116, y, value, TEXT, 11.5), '</g>']
    parts += [text(24, 357, '$ keep learning. keep building.', MUTED, 11)]
    save_svg(ROOT / 'assets/info-card.svg', parts)


def render_heatmap(data):
    days = data['days']
    first = date.fromisoformat(days[0]['date'])
    start = first - timedelta(days=(first.weekday()+1) % 7)
    last = date.fromisoformat(days[-1]['date'])
    weeks = (last-start).days // 7 + 1
    step = min(15, 814 / weeks)
    cell = step - 3
    parts = svg_start(900, 264, 'Shreyash Dhakate contribution calendar', f"{data['total']:,} public-calendar contributions from {days[0]['date']} to {days[-1]['date']}.")
    parts += [text(65, 24, './contributions.sh', MUTED, 11), text(24, 59, 'A year of building', TEXT, 20), text(876, 57, f"{data['total']:,} contributions", ACCENT, 14, 'text-anchor="end"')]
    used_months = set()
    for item in days:
        current = date.fromisoformat(item['date'])
        week, row = divmod((current-start).days, 7)
        x, y = 59 + week*step, 94 + row*15
        month_key = (current.year, current.month)
        if month_key not in used_months and (current.day <= 7 or not used_months):
            parts.append(text(x, 83, calendar.month_abbr[current.month], MUTED, 10))
            used_months.add(month_key)
        title = f"{current.isoformat()}: {item['count']} contribution(s)"
        parts.append(f'<rect x="{x:.2f}" y="{y}" width="{cell:.2f}" height="12" rx="2" fill="{PALETTE[item["level"]]}"><title>{escape(title)}</title>{reveal(.1 + week*.015+row*.035,.25)}</rect>')
    for row, label in [(1,'Mon'), (3,'Wed'), (5,'Fri')]:
        parts.append(text(24, 103+row*15, label, MUTED, 10))
    parts += [f'<path d="M24 213 H876" stroke="{BORDER}"/>', text(24, 239, f"{data['active_days']} active days  /  best day: {data['best_day']} contributions", MUTED, 11)]
    parts += [text(876, 239, f"updated {data['fetched_at'][:10]} UTC", MUTED, 10, 'text-anchor="end"')]
    parts += [text(709, 205, 'Less', MUTED, 9)]
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{739+i*15}" y="196" width="11" height="11" rx="2" fill="{color}"/>')
    parts += [text(820, 205, 'More', MUTED, 9)]
    save_svg(ROOT / 'assets/contrib-heatmap.svg', parts)


def render_portrait(source):
    # Pillow is only needed when changing the portrait, never by the daily job.
    from PIL import Image, ImageEnhance, ImageOps
    image = Image.open(source).convert('RGB')
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]
            # This user's existing avatar has a solid yellow background.
            if r > 160 and g > 140 and b < 140 and min(r, g) > b * 1.5:
                pixels[x, y] = (255, 255, 255)
    image = ImageEnhance.Contrast(ImageOps.autocontrast(ImageOps.grayscale(image))).enhance(1.25)
    columns, rows = 76, 62
    image = ImageOps.fit(image, (columns, rows), method=Image.Resampling.LANCZOS)
    ramp = ' .,:;+=*#%@'
    parts = svg_start(360, 370, 'ASCII portrait of Shreyash Dhakate', 'A monochrome typing portrait generated from my GitHub avatar.')
    parts += [text(65, 24, './whoami', MUTED, 11), '<defs>']
    for y in range(rows):
        parts.append(f'<clipPath id="r{y}"><rect x="16" y="{45+y*4.8-5}" width="328" height="6"><animate attributeName="width" from="0" to="328" begin="{y*.025:.3f}s" dur=".14s" fill="freeze"/></rect></clipPath>')
    parts.append('</defs>')
    for y in range(rows):
        line = ''.join(ramp[round((255-image.getpixel((x,y)))/255*(len(ramp)-1))] for x in range(columns))
        parts.append(text(16, 45+y*4.8, line, '#c9d1d9', 6.9, f'xml:space="preserve" textLength="328" lengthAdjust="spacingAndGlyphs" clip-path="url(#r{y})"'))
    parts += [text(20, 357, '> ShreyashDhakate', ACCENT, 11)]
    save_svg(ROOT / 'assets/shreyash-ascii.svg', parts)


def fetch_days(username, html_file):
    if not re.fullmatch(r'[A-Za-z0-9-]{1,39}', username):
        raise ValueError('Invalid GitHub username.')
    if html_file:
        raw = Path(html_file).read_text(encoding='utf-8')
    else:
        request = urllib.request.Request(f'https://github.com/users/{username}/contributions', headers={'User-Agent': 'github-profile-svg/1.0', 'Accept': 'text/html'})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode('utf-8')
    parser = ContributionParser()
    parser.feed(raw)
    return parser.days()


def validate_calendar_visibility(days, previous):
    """Reject a narrower feed that would erase a large part of saved history."""
    current = {day['date']: day['count'] for day in days}
    active = [day for day in previous['days']
              if day['count'] > 0 and day['date'] in current]
    erased = [day for day in active if current[day['date']] == 0]
    if len(erased) >= 10 and len(erased) * 2 >= len(active):
        raise ValueError(
            f'The feed would erase {len(erased)} of {len(active)} known active days. '
            'Its contribution visibility does not match the saved calendar.'
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html-file', help='Use a saved public contribution HTML response for validation.')
    parser.add_argument('--portrait', type=Path, help='Regenerate the portrait from a photo (requires Pillow).')
    parser.add_argument('--no-fetch', action='store_true', help='Render the saved contribution snapshot without networking.')
    args = parser.parse_args()
    profile = json.loads((ROOT/'profile.json').read_text())
    snapshot = ROOT/'data/contributions.json'
    if args.no_fetch:
        data = json.loads(snapshot.read_text())
    else:
        days = fetch_days(profile['username'], args.html_file)
        data = {
            'username': profile['username'],
            'source': f"https://github.com/users/{profile['username']}/contributions",
            'fetched_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'total': sum(day['count'] for day in days),
            'active_days': sum(day['count'] > 0 for day in days),
            'best_day': max(day['count'] for day in days), 'days': days,
        }
        if snapshot.exists():
            previous = json.loads(snapshot.read_text())
            try:
                validate_calendar_visibility(days, previous)
            except ValueError as error:
                print(f'{error} Retaining snapshot from {previous["fetched_at"]}.')
                data = previous
    # Parse and validate before writing: a changed GitHub page must not erase real data.
    render_heatmap(data)
    render_info(profile)
    if args.portrait:
        render_portrait(args.portrait)
    if not args.no_fetch:
        snapshot.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    print(f"Rendered {len(data['days'])} real days, {data['total']:,} contributions.")


if __name__ == '__main__':
    main()

