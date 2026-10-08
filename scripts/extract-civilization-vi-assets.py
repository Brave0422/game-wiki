# @author Brave
# @date 2026-10-05T13:14:32+08:00
# @description 为文明 VI 百科保存真实游戏图标、原始羊皮纸和地图纹理，并记录图片来源。
"""Download Civilopedia's original game art, with local ARX portrait fallbacks.

The installed game stores its main texture atlases in CIVBLP containers. The
Civilopedia website publishes those same game icons as individual PNG files.
This script only reads the installation and writes assets inside the project.
It requires Python's standard library only; already downloaded images are reused.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import struct
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / 'public/images/civilization-vi'
REMOTE_BASE = 'https://static.civilopedia.net/images/core/'
DEFAULT_GAME = Path("E:/SteamLibrary/steamapps/common/Sid Meier's Civilization VI")
THEMES = (
    'parchment_patternbright', 'civilopedia_chapterheader', 'compass',
    'civilopedia_portraitsquare', 'civilopedia_pageheader',
    'civilopedia_topicheader', 'pageframe',
    'icon_civilopedia_concepts', 'icon_civilopedia_civilizations',
    'icon_civilopedia_citystates', 'icon_civilopedia_districts',
    'icon_civilopedia_buildings', 'icon_civilopedia_wonders',
    'icon_civilopedia_units', 'icon_civilopedia_unitpromotions',
    'icon_civilopedia_greatpeople', 'icon_civilopedia_technologies',
    'icon_civilopedia_civics', 'icon_civilopedia_governments',
    'icon_civilopedia_religions', 'icon_civilopedia_features',
    'icon_civilopedia_resources', 'icon_civilopedia_improvements',
    'icon_civilopedia_governors', 'icon_civilopedia_historic_moments',
)
THEME_ALIASES = {
    'parchment-pattern': 'parchment_patternbright',
    'chapter-header': 'civilopedia_chapterheader',
}


def png_info(path: Path) -> dict:
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'Invalid PNG: {path.name}')
    width, height = struct.unpack('>II', data[16:24])
    return {'width': width, 'height': height, 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def download(filename: str, source_name: str, retries: int = 2, refresh: bool = False) -> dict:
    destination = ASSET_DIR / filename
    url = REMOTE_BASE + source_name.lower() + '.png'
    if refresh or not destination.exists():
        for attempt in range(retries + 1):
            try:
                request = urllib.request.Request(url, headers={
                    'User-Agent': 'GameWikiAssetImporter/1.0',
                    'Referer': 'https://www.civilopedia.net/',
                })
                with urllib.request.urlopen(request, timeout=25) as response:
                    data = response.read()
                if data[:8] != b'\x89PNG\r\n\x1a\n':
                    raise ValueError('Response is not a PNG')
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                break
            except urllib.error.HTTPError as error:
                if error.code == 404 or attempt == retries:
                    return {'error': f'HTTP {error.code}', 'source': url}
                time.sleep(0.4 * (attempt + 1))
            except (OSError, ValueError) as error:
                if attempt == retries:
                    return {'error': str(error), 'source': url}
                time.sleep(0.4 * (attempt + 1))
    return {'path': '/images/civilization-vi/' + filename,
            'iconName': source_name, 'source': url, **png_info(destination)}


def targets_from_manifest(path: Path) -> dict[str, str]:
    manifest = json.loads(path.read_text(encoding='utf-8'))
    records = manifest if isinstance(manifest, list) else manifest.get('entries', [])
    if isinstance(records, dict):
        records = list(records.values())
    targets = {}
    for entry in records:
        source_type = entry.get('sourceType') or entry.get('type')
        if source_type:
            targets[source_type] = entry.get('iconName') or 'ICON_' + source_type
    return targets


def targets_from_game(game_dir: Path) -> dict[str, str]:
    prefixes = ('ICON_CIVILIZATION_', 'ICON_LEADER_', 'ICON_UNIT_',
                'ICON_BUILDING_', 'ICON_DISTRICT_', 'ICON_TECH_', 'ICON_CIVIC_',
                'ICON_RESOURCE_', 'ICON_POLICY_', 'ICON_GOVERNMENT_',
                'ICON_IMPROVEMENT_', 'ICON_FEATURE_', 'ICON_TERRAIN_',
                'ICON_BELIEF_', 'ICON_PROMOTION_', 'ICON_GREAT_PERSON_')
    targets = {}
    for path in game_dir.rglob('*Icons*.xml'):
        for row in ET.parse(path).findall('.//IconDefinitions/Row'):
            icon_name = row.get('Name', '')
            if icon_name.startswith(prefixes) and not icon_name.endswith('_FOW'):
                targets[icon_name.removeprefix('ICON_')] = icon_name
    return targets


def game_icon_aliases(game_dir: Path) -> dict[str, tuple[str, str]]:
    aliases = {}
    for path in game_dir.rglob('*Icons*.xml'):
        # Scenario packages replace ordinary leader portraits with their civ
        # emblems. Their aliases must not enter the standard game encyclopedia.
        if any('scenario' in part.lower() for part in path.parts):
            continue
        for row in ET.parse(path).findall('.//IconAliases/Row'):
            if row.get('Name') and row.get('OtherName'):
                aliases[row.get('Name')] = (row.get('OtherName'), str(path))
    return aliases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-dir', type=Path, default=DEFAULT_GAME)
    parser.add_argument('--manifest', type=Path,
                        default=ROOT / 'app/data/civilization-vi.source.json')
    parser.add_argument('--themes-only', action='store_true')
    parser.add_argument('--from-game-icons', action='store_true')
    parser.add_argument('--types', nargs='+', help='Download selected game Type identifiers only')
    parser.add_argument('--workers', type=int, default=12)
    args = parser.parse_args()
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = ASSET_DIR / 'image-map.json'
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    assets = previous.get('assets', {})
    targets = {} if args.themes_only else (
        {name: 'ICON_' + name for name in args.types} if args.types
        else targets_from_game(args.game_dir) if args.from_game_icons
        else targets_from_manifest(args.manifest))
    aliases = game_icon_aliases(args.game_dir) if targets else {}
    jobs = {name: (name + '.png', name) for name in THEMES}
    jobs.update({source_type: (source_type + '.png', aliases.get(icon_name, (icon_name, ''))[0])
                 for source_type, icon_name in targets.items()})
    grouped_jobs = {}
    for key, (filename, icon_name) in jobs.items():
        grouped_jobs.setdefault(icon_name.lower(), []).append((key, filename, icon_name))
    failures = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = {executor.submit(download, group[0][1], group[0][2],
                                   refresh=assets.get(group[0][0], {}).get('iconName', '').lower() not in ('', group[0][2].lower())): group
                   for group in grouped_jobs.values()}
        for index, future in enumerate(as_completed(pending), 1):
            group = pending[future]
            result = future.result()
            for key, filename, icon_name in group:
                if 'error' in result:
                    failures[key] = result
                else:
                    source_file = ROOT / 'public' / result['path'].lstrip('/')
                    destination = ASSET_DIR / filename
                    if source_file != destination:
                        shutil.copyfile(source_file, destination)
                    assets[key] = {**result, 'path': '/images/civilization-vi/' + filename,
                                   'iconName': icon_name}
                    requested_icon = targets.get(key)
                    if requested_icon in aliases:
                        assets[key].update({'requestedIconName': requested_icon,
                                            'aliasSource': aliases[requested_icon][1]})
            if index % 100 == 0 or index == len(pending):
                print(f'{index}/{len(pending)} distinct images processed; {len(failures)} unavailable', flush=True)
    # ARX contains actual shipped leader portraits for offline recovery.
    local_portraits = {path.stem.removeprefix('Civ_'): path
                      for path in args.game_dir.rglob('Civ_LEADER_*.png')}
    for key in list(failures):
        if key not in local_portraits:
            continue
        original = local_portraits[key]
        destination = ASSET_DIR / (key + '.png')
        shutil.copyfile(original, destination)
        assets[key] = {'path': '/images/civilization-vi/' + destination.name,
                       'source': str(original), 'iconName': targets[key],
                       **png_info(destination)}
        del failures[key]
    for alias, original_name in THEME_ALIASES.items():
        if original_name not in assets:
            continue
        shutil.copyfile(ASSET_DIR / (original_name + '.png'), ASSET_DIR / (alias + '.png'))
        assets[alias] = {**assets[original_name], 'path': '/images/civilization-vi/' + alias + '.png'}
    result = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'sourceSite': 'https://www.civilopedia.net/zh-CN/gathering-storm/concepts/intro/',
        'copyright': 'Civilization VI game art © Firaxis Games / 2K Games; original assets retained for encyclopedic reference.',
        'images': {key: value['path'] for key, value in sorted(assets.items())},
        'assets': dict(sorted(assets.items())),
        'unavailable': dict(sorted(failures.items())),
    }
    manifest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Saved {len(assets)} verified PNGs; {len(failures)} unavailable', flush=True)


if __name__ == '__main__':
    main()
