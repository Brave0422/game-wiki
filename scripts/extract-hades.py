# @author Brave
# @date 2026-10-04T21:52:13+08:00
# @description 从哈迪斯 PC 游戏的 Lua、中文 SJSON 与图集只读生成祝福和武器形态百科。
# 依赖：pillow lz4 sjson lupa，以及 https://github.com/quaerus/deppth
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

import sjson
from lupa import LuaRuntime, lua_type
from deppth.sggpio import PackageWithManifestReader

ROOT = Path(__file__).resolve().parent.parent
BASES = {}
RARITIES = ('Common', 'Rare', 'Epic', 'Heroic', 'Legendary')
GODS = {'Zeus': '宙斯', 'Poseidon': '波塞冬', 'Athena': '雅典娜', 'Aphrodite': '阿佛洛狄忒', 'Artemis': '阿尔忒弥斯', 'Ares': '阿瑞斯', 'Dionysus': '狄俄尼索斯', 'Demeter': '得墨忒耳', 'Hermes': '赫尔墨斯', 'Trial': '混沌', 'Hades': '哈迪斯'}
KEYWORDS = {'Attack': '攻击', 'Special': '特殊攻击', 'Cast': '投弹', 'Rush': '冲刺', 'BlinkStrike': '冲刺攻击', 'BlinkSpecial': '冲刺特殊攻击', 'Crit': '暴击', 'Shout': '援助', 'Super': '神力', 'Chill': '冰冷', 'Cloud': '霜冻酒雾', 'Doom': '厄运', 'Weak': '虚弱', 'Deflect': '反弹', 'Poison': '醉酒', 'Rupture': '撕裂', 'Jolted': '感电', 'Jolt': '感电', 'Spin': '旋转攻击', 'Tackle': '蛮牛冲撞', 'ManualReload': '手动装填', 'Armor': '护甲', 'DeathDefiance': '死里逃生', 'Ammo': '血石', 'Health': '生命值'}
WEAPON_INFO = {
    'SwordWeapon': ('Stygius · Stygian Blade', '近战三连斩，特殊攻击为周身范围震击；可以用冲刺攻击快速贴近敌人。初始武器，无需钥匙解锁。', 0),
    'SpearWeapon': ('Varatha · Eternal Spear', '攻击可远距离突刺，长按可蓄力旋转；特殊攻击投出长矛，再次使用将其召回。', 4),
    'ShieldWeapon': ('Aegis · Shield of Chaos', '攻击挥盾，长按可格挡正面攻击并蓄力发动蛮牛冲撞；特殊攻击投盾，盾牌可弹射后返回。', 3),
    'BowWeapon': ('Coronacht · Heart-Seeking Bow', '长按攻击蓄力射箭，在合适时机释放可发动强力射击；特殊攻击向前扇形射出多支箭。', 1),
    'FistWeapon': ('Malphon · Twin Fists', '攻击为快速连续拳击，特殊攻击为上勾拳；冲刺后可衔接冲刺攻击和冲刺特殊攻击。', 8),
    'GunWeapon': ('Exagryph · Adamant Rail', '攻击连射并消耗弹药，可手动装填；特殊攻击向选定区域发射爆炸榴弹。', 8),
}
HIDDEN_UNLOCKS = {
    'SwordConsecrationTrait': '先揭示关羽形态，并在冥界之刃上累计投入至少 5 份泰坦之血；与倪克斯交谈取得唤醒密语，再在武器架揭示。',
    'SpearSpinTravel': '购买承包商的命运清单，至少用泰坦之血解锁 5 个非扎格列欧斯形态，并到达最终首领；与阿喀琉斯交谈取得唤醒密语，再在武器架揭示。',
    'ShieldLoadAmmoTrait': '先揭示关羽形态，并在混沌之盾上累计投入至少 5 份泰坦之血；持盾与混沌交谈触发相关对话，再取得唤醒密语。',
    'BowBondTrait': '先揭示关羽形态，并在索心弓上累计投入至少 5 份泰坦之血；持弓与阿尔忒弥斯触发相关对话，再取得唤醒密语。',
    'FistDetonateTrait': '先揭示关羽形态，并在双子之拳上累计投入至少 5 份泰坦之血；持拳套遇到阿斯忒里俄斯的单独战斗，触发相关对话并取得唤醒密语。',
    'GunLoadedGrenadeTrait': '先揭示关羽形态，并在狮鹫坚炮上累计投入至少 5 份泰坦之血；与宙斯交谈取得唤醒密语，再在武器架揭示。',
}


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sequence(value) -> list:
    return value if isinstance(value, list) else []


def plain(value):
    if lua_type(value) == 'table':
        keys = list(value.keys())
        if keys and set(keys) == set(range(1, len(keys) + 1)):
            return [plain(value[i]) for i in range(1, len(keys) + 1)]
        return {key: plain(item) for key, item in value.items()}
    return value


def merge(first: dict, second: dict) -> dict:
    result = copy.deepcopy(first)
    for key, value in second.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else copy.deepcopy(value)
    return result


def inherited(key: str, table: dict) -> dict:
    data = table.get(key, {})
    result = {}
    parents = data.get('InheritFrom', [])
    for parent in [parents] if isinstance(parents, str) else parents:
        if parent != key:
            result = merge(result, inherited(parent, table))
    return merge(result, data)


def processed(value, multiplier: float = 1) -> float | None:
    if isinstance(value, (float, int)):
        return value
    if not isinstance(value, dict):
        return None
    base = value.get('BaseValue', value.get('BaseMin', value.get('ChangeValue')))
    if not isinstance(base, (float, int)):
        return None
    if value.get('IgnoreRarity') or 'ChangeValue' in value:
        multiplier = 1
    result = 1 + (base - 1) * multiplier if value.get('SourceIsMultiplier') else base * multiplier
    if value.get('SourceIsNegativeMultiplier'):
        result = 2 - base * multiplier
    if value.get('AsInt'):
        result = math.floor(result + 0.5)
    elif value.get('ToNearest'):
        result = math.floor((result + 1e-9) / value['ToNearest']) * value['ToNearest']
    return round(result + 1e-10, value.get('DecimalPlaces', 2))


def format_value(value: float | None, spec: dict) -> str | None:
    if value is None:
        return None
    kind = spec.get('Format', '')
    if kind == 'Percent': value *= 100
    elif kind == 'PercentDelta': value = (value - 1) * 100
    elif kind == 'NegativePercentDelta': value = (1 - value) * 100
    elif kind == 'AmmoDelayDivisor': value = BASES['WeaponData']['RangedWeapon']['AmmoDropDelay'] / value
    elif kind == 'AmmoReloadDivisor': value = 3 / value
    elif kind == 'Divisor': value = 1 / value
    elif kind in ('MultiplyByBase', 'PercentOfBase'):
        base = inherited(spec['BaseName'], BASES[spec['BaseType']])[spec['BaseProperty']]
        value = value * base if kind == 'MultiplyByBase' else value / base * 100
    elif kind in ('PercentHeal', 'PercentPlayerHealth'): value *= 100
    precision = int(spec.get('DecimalPlaces', 0))
    scale = 10 ** precision
    value = math.copysign(math.floor(abs(value) * scale + 0.5 + 1e-9) / scale, value)
    return f'{value:g}'


def tooltip_values(data: dict, rarity: str = 'Common') -> dict[str, str]:
    rarity_data = data.get('RarityLevels', {}).get(rarity, {})
    multiplier = rarity_data.get('Multiplier', rarity_data.get('MinMultiplier', 1))
    values, order = {}, []

    def extract(node, spec):
        value = node.get(spec.get('Key')) if 'Key' in spec else node
        custom = value.get('CustomRarityMultiplier', {}).get(rarity, {}) if isinstance(value, dict) else {}
        effective_multiplier = custom.get('Multiplier', custom.get('MinMultiplier', multiplier))
        if spec.get('External') and spec.get('BaseType') in BASES and spec.get('BaseName'):
            value = inherited(spec['BaseName'], BASES[spec['BaseType']]).get(spec['BaseProperty'])
        if spec.get('Format') == 'EXWrathDuration':
            value = processed(value, 1) * data['AddShout']['SuperDuration']
        return format_value(processed(value, effective_multiplier), spec)

    def walk(node):
        if isinstance(node, list):
            for child in node: walk(child)
        elif isinstance(node, dict):
            for spec in sequence(node.get('ExtractValues')):
                result = extract(node, spec)
                if result is not None:
                    values[spec['ExtractAs']] = result
                    if not spec.get('SkipAutoExtract') and not spec.get('External'):
                        order.append((result, spec.get('Format', '')))
            spec = node.get('ExtractValue')
            if isinstance(spec, dict):
                property_multiplier = multiplier
                overrides = node.get('RarityMultiplier', {})
                if isinstance(overrides, dict) and rarity in overrides:
                    property_multiplier = overrides[rarity].get('Multiplier', overrides[rarity].get('MinMultiplier', multiplier))
                result = format_value(processed(node, property_multiplier), spec)
                if result is not None:
                    values[spec['ExtractAs']] = result
                    if not spec.get('SkipAutoExtract') and not spec.get('External'):
                        order.append((result, spec.get('Format', '')))
            for key, child in node.items():
                if key not in ('ExtractValues', 'ExtractValue', 'RarityLevels'):
                    walk(child)
    walk(data)
    for index, (value, kind) in enumerate(order, 1):
        rendered = value + ('%' if kind in ('Percent', 'PercentDelta', 'NegativePercentDelta', 'PercentHeal', 'PercentOfBase', 'PercentPlayerHealth') else '')
        values[f'DisplayDelta{index}'] = rendered
        values[f'NewTotal{index}'] = rendered
        values[f'NewTotal[{index}]'] = rendered
        values[f'OldTotal{index}'] = '0'
        values[f'OldTotal[{index}]'] = '0'
    def expose(node, path=''):
        if not isinstance(node, dict): return
        for key, value in node.items():
            full_path = path + str(key)
            numeric = processed(value, multiplier)
            if numeric is not None:
                values.setdefault(full_path, f'{numeric:g}')
            if isinstance(value, dict): expose(value, full_path + '.')
    expose(data)
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-dir', type=Path, default=Path('E:/SteamLibrary/steamapps/common/Hades'))
    args = parser.parse_args()
    content = args.game_dir / 'Content'
    lua = LuaRuntime(unpack_returned_tuples=True)
    # 数据表只引用其它全局表；空引用用于跳过本轮无需读取的语音与动画组。
    lua.execute('function empty() return setmetatable({}, {__index=function(t,k) local v=empty(); rawset(t,k,v); return v end}) end; setmetatable(_G,{__index=function(t,k) local v=empty(); rawset(t,k,v); return v end})')
    lua.execute('function ToLookup(value) return value end')
    tables = {}
    for filename in ('TraitData', 'LootData', 'WeaponUpgradeData', 'WeaponData'):
        lua.execute((content / f'Scripts/{filename}.lua').read_text(encoding='utf-8-sig'))
        tables[filename] = plain(lua.globals()[filename])
    traits, loot, weapons = (tables[name] for name in ('TraitData', 'LootData', 'WeaponUpgradeData'))
    BASES['WeaponData'] = tables['WeaponData']
    for family, field in (('Weapons', 'Weapon'), ('Projectiles', 'Projectile')):
        BASES[field] = {}
        for path in sorted((content / f'Game/{family}').glob('*.sjson')):
            items = sjson.loads(path.read_text(encoding='utf-8-sig'))
            BASES[field].update({item['Name']: item for item in items.get(family, [])})
    BASES['ProjectileBase'] = BASES['Projectile']
    BASES['Effect'] = {}
    for item in BASES['Projectile'].values():
        if not item['Name'].startswith('1_Base'): continue
        for effect in sequence(item.get('Effects')):
            BASES['Effect'].setdefault(effect['Name'], effect)
    text = {}
    for lang in ('zh-CN', 'en'):
        source = sjson.loads((content / f'Game/Text/{lang}/HelpText.{lang}.sjson').read_text(encoding='utf-8'))
        text[lang] = {entry['Id']: entry for entry in source['Texts']}

    def localized(key: str, field: str = 'DisplayName', lang: str = 'zh-CN') -> str:
        return inherited(key, text[lang]).get(field, '')

    unresolved = []
    def clean(value: str, values: dict | None = None, key: str = '') -> str:
        values = values or {}
        value = re.sub(r'\\Column\s+\d+', '', value)
        def replace(match):
            family, name = match.group(1), match.group(2).split(':')[0]
            if family == 'Keywords':
                return KEYWORDS.get(name, re.sub(r'\{[^}]+\}', '', localized(name)) or name)
            if family == 'TooltipData':
                if name in values:
                    return values[name] + ('%' if ':' in match.group(2) and match.group(2).split(':')[-1].lower() == 'p' else '')
                unresolved.append({'id': key, 'token': name})
                return '〔数值〕'
            if family == 'HeroData' and name == 'DefaultHero.ComboThreshold': return '12'
            unresolved.append({'id': key, 'token': family + '.' + name})
            return '〔数值〕'
        value = re.sub(r'\{\$([\w]+)\.([^}]+)\}', replace, value)
        icon_names = {'Ammo': '血石', 'RightArrow': ' → ', 'Health': '生命值', 'HealthUp': '生命上限', 'HealthUp_Small': '', 'HealthDown_Small': '生命上限', 'HealthRestoreHome': '生命回复', 'Money': '金币', 'MetaPoint': '黑暗', 'MetaPoints': '黑暗', 'Gem': '宝石', 'Gems': '宝石'}
        value = re.sub(r'\{!Icons\.([^}]+)\}', lambda match: icon_names.get(match[1], ''), value)
        value = value.replace('{!Icons.HealthDown_Small}', '生命上限').replace('{!Icons.HealthRestoreHome}', '生命回复')
        value = re.sub(r'\{[^}]+\}', '', value)
        value = re.sub(r'\\Column\s+\d+', '', value)
        return re.sub(r'[ \t]+', ' ', value).replace('%%', '%').strip()

    # 每张输出图片明确记录动画名 → FilePath → 图集裁剪矩形的对应关系。
    animations = {}
    for filename in ('GUIAnimations.sjson', 'PortraitAnimations.sjson'):
        animation_text = (content / 'Game/Animations' / filename).read_text(encoding='utf-8')
        animation_text = re.sub(r'(FilePath\s*=\s*")([^"]*)(")', lambda match: match[1] + match[2].replace('\\', '\\\\') + match[3], animation_text)
        values = sjson.loads(animation_text)
        animations.update({entry['Name']: entry for entry in values['Animations']})
    wanted, image_sources = {}, []
    def register_image(animation: str, key: str) -> str:
        variant = animation + '_Large' if animation + '_Large' in animations else animation
        definition = inherited(variant, animations)
        if not definition.get('FilePath'):
            raise ValueError(f'缺少实际图片引用：{animation}')
        wanted.setdefault(definition['FilePath'], []).append(key)
        return f'/images/hades/{key}.png'

    entries, rules_by_trait, providers = [], {}, {}
    for god, god_name in GODS.items():
        pool = loot[god + 'Upgrade']
        ids = sequence(pool.get('WeaponUpgrades')) + sequence(pool.get('Traits')) + list(pool.get('LinkedUpgrades', {}))
        if god == 'Trial': ids = sequence(pool.get('PermanentTraits'))
        for key in ids:
            providers.setdefault(key, []).append(god_name)
            if key in pool.get('LinkedUpgrades', {}): rules_by_trait[key] = pool['LinkedUpgrades'][key]
    providers['HadesShoutTrait'] = ['哈迪斯']
    def names(keys): return '、'.join(f'「{clean(localized(key))}」' for key in keys)
    def requirements(rule):
        lines = []
        if rule.get('OneOf'): lines.append('至少持有其中一项：' + names(rule['OneOf']))
        if rule.get('OneFromEachSet'):
            lines.append('以下各组都至少持有一项：\n' + '\n'.join(f'{i + 1}. {names(group)}' for i, group in enumerate(rule['OneFromEachSet'])))
        return '\n'.join(lines)
    for key, gods in providers.items():
        data = inherited(key, traits)
        if not localized(key) or not data.get('Icon'):
            raise ValueError(f'祝福缺少名称或图标：{key}')
        own_rarities = traits[key].get('RarityLevels', data.get('RarityLevels', {}))
        rarity = 'Legendary' if own_rarities and 'Common' not in own_rarities else 'Common'
        values = tooltip_values(data, rarity)
        if key == 'ShieldLoadAmmo_DionysusRangedTrait':
            values['DisplayDelta2'] = values['TooltipDamage']
            values['NewTotal2'] = values['TooltipDamage']
        description = clean(localized(key, 'Description') or localized(key + '_Tray', 'Description'), values, key)
        god = next(god for god, name in GODS.items() if name == gods[0])
        is_duo = bool(data.get('IsDuoBoon'))
        is_legendary = not is_duo and (data.get('Frame') == 'Legendary' or rarity == 'Legendary')
        tags = [*dict.fromkeys(gods), '双重祝福' if is_duo else '传奇祝福' if is_legendary else '普通祝福']
        if key.startswith('ShieldLoadAmmo_'): tags.append('贝奥武夫形态')
        slot = {'Melee': '攻击', 'Secondary': '特殊攻击', 'Ranged': '投弹', 'Rush': '冲刺', 'Shout': '援助'}.get(data.get('Slot'))
        if slot: tags.append(slot)
        acquisition = '在逃脱过程中选择对应神祇符号的房间奖励，或在卡戎商店购买对应祝福。满足前置条件后才可能进入本次选项，出现并不保证。'
        if god not in ('Hermes', 'Trial', 'Hades'):
            acquisition += f'使用{gods[0]}的信物，可以让下一次普通神祇祝福优先来自该神；双重祝福也可由相关的另一位神提供。' if is_duo else f'使用{gods[0]}的信物，可以让下一次普通神祇祝福优先来自该神。'
        if god == 'Demeter': acquisition += '需先到达地表的最终首领房间，得墨忒耳才会加入祝福池。'
        if god == 'Hermes': acquisition += '赫尔墨斯的奖励独立于常规奥林匹斯神池，通常在逃脱流程中出现。'
        if god == 'Trial':
            acquisition = '进入混沌之门，支付入口生命代价并选择混沌恩赐；持宇宙之卵可免除入口生命代价。先承受随机诅咒规定的遭遇次数，随后获得该永久增益。'
        if god == 'Hades':
            acquisition = '与哈迪斯的好感达到赠予信物条件，赠送蜜露取得冥王印玺；装备它后获得专属援助，无法同时拥有普通奥林匹斯援助。'
        prerequisite = requirements(rules_by_trait.get(key, {}))
        extras = []
        if data.get('RequiredTrait'): extras.append('需要持有：' + names([data['RequiredTrait']]))
        if data.get('RequiredOneOfTraits'): extras.append('需要持有其中一项：' + names(data['RequiredOneOfTraits']))
        false_traits = [name for name in sequence(data.get('RequiredFalseTraits')) if name != key]
        if false_traits: extras.append('不能同时持有：' + names(false_traits))
        if data.get('RequiredWeapon'): extras.append('限定武器：' + clean(localized(data['RequiredWeapon'])))
        if data.get('RequiredFalseTrait') and data['RequiredFalseTrait'] != key: extras.append('不能同时持有：' + names([data['RequiredFalseTrait']]))
        if data.get('RequiredMetaUpgradeSelected'): extras.append('冥夜之镜必须选择：' + clean(localized(data['RequiredMetaUpgradeSelected'])))
        if data.get('RequiredSlottedTrait') == 'Shout': extras.append('需要先获得一项援助祝福。')
        special = '\n'.join(filter(None, [prerequisite, *extras]))
        entry = {'id': f'hades-{key}', 'category': 'boons', 'name': clean(localized(key)), 'englishName': clean(localized(key, lang='en')),
                 'description': description, 'image': register_image(data['Icon'], key), 'tags': tags, 'acquisition': acquisition,
                 'notes': ['作用数值按初始等级、普通稀有度（传奇或双重祝福采用其固定稀有度）展示；强化与更高稀有度会改变可成长属性。']}
        if special: entry['specialAcquisition'] = special
        entries.append(entry)

    aspect_sources = []
    for weapon, (english_name, description, keys) in WEAPON_INFO.items():
        aspects = []
        for index, config in enumerate(weapons[weapon]):
            key = config.get('TraitName', config.get('RequiredInvestmentTraitName'))
            data = inherited(key, traits)
            values = tooltip_values(data)
            short = localized(key + '_Tray', 'Description') or localized(key, 'Description').split('\n\n')[0]
            property_match = re.search(r'\{#PropertyFormat\}(.*)', short, re.S)
            label = clean(property_match[1].split('\\Column')[0], values, key).rstrip('：:') if property_match else '形态属性'
            token = re.findall(r'\{\$TooltipData\.([^}:]+)(?::[^}]*)?\}', property_match[1] if property_match else short)
            upgrade_token = token[-1] if token else ''
            if key == 'BowLoadAmmoTrait': upgrade_token = 'TooltipAmmo'
            levels = []
            previous = None
            for level, rarity in enumerate(RARITIES, 1):
                current = tooltip_values(data, rarity)
                value = current.get(upgrade_token)
                if value is None: raise ValueError(f'形态升级属性无法解析：{key} / {upgrade_token}')
                unit = '%' if re.search(r'\{\$TooltipData\.' + re.escape(upgrade_token) + r':[pP]\}', short) or key in ('SpearSpinTravel', 'BowBondTrait') else ' 秒' if key == 'BowLoadAmmoTrait' else ''
                num = float(value)
                delta = '首次解锁' if previous is None else ('减少 ' if num < previous else '增加 ') + f'{abs(round(num - previous, 2)):g}' + (' 个百分点' if unit == '%' else unit)
                levels.append({'level': level, 'value': value + unit, 'delta': delta, 'cost': config['Costs'][level - 1]})
                previous = num
            acquisition = HIDDEN_UNLOCKS.get(key, '解锁全部六种武器并推进逃脱，开启形态系统后，在武器架消耗泰坦之血解锁或升级。')
            aspects.append({'id': key, 'name': clean(localized(key)), 'image': register_image(config['Image'], key + '-portrait'),
                            'description': clean(short.split('{!Icons.Bullet}')[0], values, key), 'acquisition': acquisition,
                            'upgradeLabel': label, 'levels': levels})
            aspect_sources.append({'id': key, 'weapon': weapon, 'configuration': config, 'tooltipKey': upgrade_token})
        entries.append({'id': 'hades-' + weapon, 'category': 'weapons', 'name': clean(localized(weapon)), 'englishName': english_name,
                        'description': description, 'image': aspects[0]['image'], 'tags': ['近战' if weapon in ('SwordWeapon', 'FistWeapon') else '近战与投掷' if weapon in ('SpearWeapon', 'ShieldWeapon') else '远程', '4 种形态'],
                        'acquisition': '初始解锁。' if not keys else f'在武器架消耗 {keys} 把冥府钥匙解锁。' + ('需先解锁其它五种武器。' if weapon == 'GunWeapon' else ''), 'aspects': aspects})

    image_dir = ROOT / 'public/images/hades'
    image_dir.mkdir(parents=True, exist_ok=True)
    found = set()
    with PackageWithManifestReader(str(content / 'Win/Packages/GUI.pkg')) as package:
        for atlas in package:
            manifest = atlas.manifest_entry
            if not manifest or not hasattr(manifest, 'subAtlases'): continue
            selections = [sprite for sprite in manifest.subAtlases if sprite['name'] in wanted]
            if not selections: continue
            image = atlas._get_image()
            for sprite in selections:
                rect = sprite['rect']
                result = image.crop((rect['x'], rect['y'], rect['x'] + rect['width'], rect['y'] + rect['height']))
                result.thumbnail((256, 256))
                for name in wanted[sprite['name']]: result.save(image_dir / f'{name}.png', optimize=True)
                found.add(sprite['name'])
                image_sources.append({'sprite': sprite['name'], 'atlas': atlas.name, 'rect': rect, 'outputs': wanted[sprite['name']]})
    if missing := set(wanted) - found: raise ValueError(f'图集缺图：{sorted(missing)}')
    save(ROOT / 'app/data/hades.entries.json', entries)
    save(ROOT / 'app/data/hades.source.json', {
        'createdAt': datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
        'source': '用户提供的 Hades PC 安装目录，只读提取 TraitData、LootData、WeaponUpgradeData、HelpText 与 GUI 图集',
        'counts': dict(Counter(entry['category'] for entry in entries)), 'aspects': aspect_sources,
        'files': {name: hashlib.sha256((content / f'Scripts/{name}.lua').read_bytes()).hexdigest() for name in tables},
        'images': image_sources, 'linkedRequirements': rules_by_trait, 'unresolvedTokens': unresolved,
    })
    print(json.dumps({'counts': dict(Counter(entry['category'] for entry in entries)), 'images': len(found), 'unresolvedTokens': len(unresolved)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
