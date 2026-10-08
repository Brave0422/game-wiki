# @author Brave
# @date 2026-10-05T13:18:09+08:00
# @description 只读解析文明 VI 原版与 DLC 的 XML/SQL，按风云变幻规则生成中文百科。
"""Reproduce the local Civilopedia catalogue using Python's standard library.

The game installation is read only. XML database operations are applied to an
in-memory SQLite database in mod action load order; scenario/mode actions are
excluded. Chinese localization is taken from the same active mod actions.
Images are resolved by the separate image extraction manifest when available.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GAME = Path("E:/SteamLibrary/steamapps/common/Sid Meier's Civilization VI")
CATEGORIES = {
    'civilizations': ('Civilizations', 'CivilizationType', '文明'),
    'leaders': ('Leaders', 'LeaderType', '领袖'),
    'units': ('Units', 'UnitType', '单位'),
    'buildings': ('Buildings', 'BuildingType', '建筑'),
    'wonders': ('Buildings', 'BuildingType', '奇观'),
    'districts': ('Districts', 'DistrictType', '区域'),
    'technologies': ('Technologies', 'TechnologyType', '科技'),
    'civics': ('Civics', 'CivicType', '市政'),
    'resources': ('Resources', 'ResourceType', '资源'),
    'concepts': ('CivilopediaPages', 'PageId', '机制'),
}
ICONS = {
    'Gold': '金币', 'Science': '科技值', 'Culture': '文化值', 'Faith': '信仰值',
    'Food': '食物', 'Production': '生产力', 'Tourism': '旅游业绩', 'Housing': '住房',
    'Amenities': '宜居度', 'Amenity': '宜居度', 'Citizen': '人口', 'Population': '人口',
    'Strength': '战斗力', 'Combat': '战斗力', 'Ranged': '远程战斗力', 'Movement': '移动力',
    'Range': '射程', 'Sight': '视野', 'Religion': '宗教', 'Religious': '宗教',
    'GreatPerson': '伟人', 'GreatProphet': '大预言家', 'GreatGeneral': '大将军',
    'GreatAdmiral': '海军统帅', 'GreatScientist': '大科学家', 'GreatEngineer': '大工程师',
    'GreatMerchant': '大商人', 'GreatWriter': '大作家', 'GreatArtist': '大艺术家',
    'GreatMusician': '大音乐家', 'GreatWork_Writing': '著作', 'GreatWork_Music': '乐曲',
    'GreatWork_Landscape': '绘画', 'GreatWork_Artifact': '文物', 'GreatWork_Relic': '遗物',
    'TradeRoute': '贸易路线', 'TradingPost': '贸易站', 'Envoy': '使者', 'Governor': '总督',
    'GovernorTitle': '总督头衔', 'Loyalty': '忠诚度', 'DiplomaticFavor': '外交支持',
    'Diplomacy': '外交', 'DiplomaticVictory': '外交胜利点数', 'Power': '电力',
    'Capital': '首都', 'CapitalCity': '首都', 'City': '城市', 'District': '区域',
    'TechBoosted': '尤里卡', 'CivicBoosted': '鼓舞', 'Eureka': '尤里卡',
    'Inspiration': '鼓舞', 'Fortified': '防御', 'Attack': '攻击', 'Defense': '防御',
    'Damage': '伤害', 'Heal': '治疗', 'Healthy': '生命值', 'Promotion': '升级',
    'Barbarian': '蛮族', 'Fortification': '防御', 'Pressure': '宗教压力',
}
GROUPS = {
    'CITIES': '城市发展', 'WORLD': '世界与地形', 'COMBAT': '战斗', 'AIRCOMBAT': '空战',
    'MOVEMENT': '单位移动', 'SCIENCE': '科技与科学', 'CULTURE': '文化与市政',
    'GOLD': '金币与经济', 'RELIGION': '信仰与宗教', 'DIPLOMACY': '外交',
    'CITY_STATES': '城邦', 'TRADE': '贸易', 'GOVERNMENT': '政体与政策',
    'GREAT_PEOPLE': '伟人', 'WMD': '核武器', 'TOURISM': '旅游业绩',
    'VICTORY': '胜利与失败', 'TEAMS': '团队', 'EXPANSION1': '迭起兴衰',
    'EXPANSION2': '风云变幻',
}


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def fields(element: ET.Element) -> dict:
    result = dict(element.attrib)
    result.update({child.tag: ''.join(child.itertext()).strip() for child in element})
    return result


def sql_name(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


class Extractor:
    def __init__(self, game: Path):
        self.game = game
        self.db = sqlite3.connect(':memory:')
        self.db.row_factory = sqlite3.Row
        self.db.create_function('Make_Hash', 1, lambda value: 0)
        self.db.create_function('LOWER', 1, lambda value: str(value).lower())
        self.text = {'zh_Hans_CN': {}, 'en_US': {}}
        self.text_sources = {}
        self.files = {}
        self.warnings = []
        self.provenance = defaultdict(set)
        self.table_columns = {}
        self.table_keys = {}
        self.missing_localization = set()
        self.localization_aliases = {}

    def record_file(self, path: Path):
        relative = path.relative_to(self.game).as_posix()
        if relative not in self.files:
            self.files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        return relative

    def columns(self, table):
        if table not in self.table_columns:
            details = list(self.db.execute(f'PRAGMA table_info({sql_name(table)})'))
            self.table_columns[table] = {row['name'] for row in details}
            self.table_keys[table] = [row['name'] for row in details if row['pk']]
        return self.table_columns[table]

    def xml_database(self, path: Path):
        relative = self.record_file(path)
        document = ET.parse(path).getroot()
        for table in document:
            if table.tag == 'Table':
                columns, keys = [], []
                for col in table:
                    detail = sql_name(col.attrib['name']) + ' ' + col.attrib.get('type', 'TEXT')
                    if col.attrib.get('notnull') == 'true': detail += ' NOT NULL'
                    if 'default' in col.attrib: detail += ' DEFAULT ' + repr(col.attrib['default'])
                    if col.attrib.get('primarykey') == 'true': keys.append(sql_name(col.attrib['name']))
                    columns.append(detail)
                if keys: columns.append('PRIMARY KEY (' + ', '.join(keys) + ')')
                self.db.execute(f'CREATE TABLE IF NOT EXISTS {sql_name(table.attrib["name"])} ({", ".join(columns)})')
                continue
            known = self.columns(table.tag)
            canonical = {column.lower(): column for column in known}
            if not known:
                self.warnings.append(f'{relative}: skipped non-gameplay table {table.tag}')
                continue
            for operation in table:
                try:
                    if operation.tag in ('Row', 'Replace', 'InsertOrIgnore'):
                        values = {canonical[key.lower()]: value for key, value in fields(operation).items() if key.lower() in canonical}
                        values = {key: (1 if value.lower() == 'true' else 0 if value.lower() == 'false' else value)
                                  for key, value in values.items()}
                        if not values: continue
                        mode = 'OR REPLACE' if operation.tag == 'Replace' else 'OR IGNORE'
                        self.db.execute(f'INSERT {mode} INTO {sql_name(table.tag)} ({", ".join(map(sql_name, values))}) '
                                        f'VALUES ({", ".join("?" for _ in values)})', list(values.values()))
                        for key in self.table_keys[table.tag]:
                            if key in values: self.provenance[(table.tag, str(values[key]))].add(relative)
                    elif operation.tag == 'Update':
                        setting = operation.find('Set')
                        where = operation.find('Where')
                        if setting is None: continue
                        updates = {canonical[key.lower()]: value for key, value in fields(setting).items() if key.lower() in canonical}
                        updates = {key: (1 if value.lower() == 'true' else 0 if value.lower() == 'false' else value)
                                   for key, value in updates.items()}
                        conditions = {canonical.get(key.lower(), key): value for key, value in fields(where).items()} if where is not None else {}
                        if not updates: continue
                        where_sql = ' AND '.join(f'{sql_name(key)} = ?' for key in conditions)
                        self.db.execute(f'UPDATE {sql_name(table.tag)} SET ' + ', '.join(f'{sql_name(key)} = ?' for key in updates)
                                        + (' WHERE ' + where_sql if where_sql else ''), list(updates.values()) + list(conditions.values()))
                        for key, value in conditions.items():
                            if key in self.table_keys[table.tag]: self.provenance[(table.tag, str(value))].add(relative)
                    elif operation.tag == 'Delete':
                        conditions = {canonical.get(key.lower(), key): value for key, value in fields(operation).items()}
                        where_sql = ' AND '.join(f'{sql_name(key)} = ?' for key in conditions)
                        self.db.execute(f'DELETE FROM {sql_name(table.tag)}' + (' WHERE ' + where_sql if where_sql else ''), list(conditions.values()))
                except sqlite3.Error as error:
                    raise RuntimeError(f'{relative}: {table.tag}/{operation.tag}: {error}') from error

    def load_database(self, path: Path):
        if path.suffix == '.sql':
            self.record_file(path)
            self.db.executescript(path.read_text(encoding='utf-8-sig'))
            self.table_columns.clear()
        else:
            self.xml_database(path)

    def load_text(self, path: Path):
        if path.suffix != '.xml': return
        relative = self.record_file(path)
        document = ET.parse(path).getroot()
        for localized in [element for element in document if element.tag in ('LocalizedText', 'BaseGameText', 'EnglishText')]:
            for row in localized:
                value = fields(row)
                language = value.get('Language', 'en_US')
                tag = value.get('Tag')
                if not tag: continue
                if row.tag == 'Delete':
                    for target_language in [language] if 'Language' in value else self.text:
                        if target_language in self.text:
                            self.text[target_language].pop(tag, None)
                            self.text_sources.pop((target_language, tag), None)
                elif language in self.text and 'Text' in value:
                    self.text[language][tag] = value['Text']
                    self.text_sources[(language, tag)] = relative

    def criterion(self, element: ET.Element | None):
        if element is None: return True
        answers = []
        for child in element:
            value = child.text or ''
            if child.tag == 'GameCoreInUse': answer = 'Expansion2' in value
            elif child.tag == 'RuleSetInUse': answer = 'RULESET_EXPANSION_2' in value
            elif child.tag == 'LeaderPlayable': answer = 'Expansion2_Players' in value or ('StandardPlayers' in value and 'Expansion' not in value)
            elif child.tag in ('GameModeEnabled', 'GameModeInUse', 'GameModeActive'): answer = False
            elif child.tag in ('HasDLC', 'DLCInUse', 'ModInUse'): answer = True
            else: answer = False
            answers.append(answer)
        return any(answers) if element.attrib.get('any') == '1' else all(answers)

    def load(self):
        base = self.game / 'Base/Assets/Gameplay/Data'
        self.load_database(base / 'Schema/01_GameplaySchema.sql')
        for path in sorted((base / 'Schema').glob('*.xml')): self.load_database(path)
        for path in sorted(base.glob('*.xml')): self.load_database(path)
        text_base = self.game / 'Base/Assets/Text'
        for path in sorted((text_base / 'en_US').glob('*.xml')): self.load_text(path)
        self.load_text(text_base / 'Vanilla_zh_Hans_CN.xml')
        actions = []
        for package in sorted((self.game / 'DLC').iterdir()):
            if not package.is_dir() or 'Scenario' in package.name or 'Mode' in package.name or package.name in ('TreeRandomizer', 'ScoutCat'): continue
            for manifest in sorted(package.glob('*.modinfo')):
                self.record_file(manifest)
                document = ET.parse(manifest).getroot()
                criteria = {element.attrib['id']: element for element in document.findall('./ActionCriteria/Criteria')}
                for index, action in enumerate(document.findall('./InGameActions/*')):
                    if action.tag not in ('UpdateDatabase', 'UpdateText'): continue
                    if not self.criterion(criteria.get(action.attrib.get('criteria'))): continue
                    load_order = int(action.findtext('./Properties/LoadOrder', '0'))
                    priority = 0 if package.name == 'Expansion2' else 1 if package.name == 'Expansion1' else 2
                    files = sorted(enumerate(action.findall('File')), key=lambda pair: (-int(pair[1].attrib.get('Priority', '0')), pair[0]))
                    actions.append((load_order, priority, package.name, index, action.tag, [package / (file.text or '') for _, file in files]))
        for _, _, _, _, kind, files in sorted(actions):
            for path in files:
                if not path.is_file():
                    self.warnings.append(f'{path.relative_to(self.game).as_posix()}: referenced optional file absent from installation')
                    continue
                (self.load_text if kind == 'UpdateText' else self.load_database)(path)

    def rows(self, table: str, **conditions):
        if not self.columns(table): return []
        if not set(conditions).issubset(self.columns(table)): return []
        where = ' AND '.join(f'{sql_name(key)} = ?' for key in conditions)
        return [dict(row) for row in self.db.execute(f'SELECT * FROM {sql_name(table)}' + (' WHERE ' + where if where else ''), list(conditions.values()))]

    def clean(self, value: str, language='zh_Hans_CN', stack=()):
        if not value: return ''
        value = str(value)
        if value.startswith('LOC_') and ' ' not in value:
            if value in stack: return ''
            translated = self.text[language].get(value)
            if translated is None:
                aliases = [value.replace('LOC_UNIT_UNIT_', 'LOC_UNIT_')]
                for prefix in ('LOC_TRAIT_CIVILIZATION_', 'LOC_TRAIT_LEADER_TRAIT_LEADER_', 'LOC_TRAIT_LEADER_'):
                    if value.startswith(prefix): aliases.append('LOC_' + value[len(prefix):])
                for trait in self.rows('Traits'):
                    for field in ('Name', 'Description'):
                        if trait.get(field) != value: continue
                        for table in ('Units', 'Buildings', 'Districts', 'Improvements'):
                            aliases.extend(item.get(field, '') for item in self.rows(table, TraitType=trait['TraitType']))
                alias = next((candidate for candidate in aliases if candidate != value and candidate in self.text[language]), None)
                if alias:
                    self.localization_aliases[value] = alias
                    translated = self.text[language][alias]
                else:
                    if language == 'zh_Hans_CN': self.missing_localization.add(value)
                    return ''
            value = self.clean(translated, language, (*stack, value))
        def replace_loc(match):
            return self.clean(match.group(1), language, stack)
        value = re.sub(r'\{(LOC_[A-Z0-9_]+)(?:[^}]*)\}', replace_loc, value)
        value = value.replace('[NEWLINE]', '\n').replace('[TAB]', ' ').replace('[SPACE]', ' ')
        def icon(match):
            key = match.group(1)
            label = ICONS.get(key, '')
            for prefix, table, type_key in (('Resource_', 'Resources', 'ResourceType'), ('Terrain_', 'Terrains', 'TerrainType'), ('Feature_', 'Features', 'FeatureType')):
                if key.lower().startswith(prefix.lower()): label = self.name(f'{prefix[:-1].upper()}_{key[len(prefix):].upper()}')
            # Most game tooltips already print the unit immediately beside its glyph.
            before, after = value[:match.start()].rstrip(), value[match.end():].lstrip()
            if label and (before.endswith(label) or after.startswith(label)): return ''
            if label in ('人口', '公民') and (after.startswith(('人口', '公民')) or before.endswith(('人口', '公民'))): return ''
            return label
        value = re.sub(r'\[ICON_([^\]]+)\]', icon, value)
        value = re.sub(r'\[/?(?:COLOR[^\]]*|BOLD|ITALIC|LINK[^\]]*|ENDLINK|ENDCOLOR|ENDCOLOR_TEXT|END_BOLD|END_ITALIC)\]', '', value, flags=re.I)
        value = re.sub(r'\[[A-Za-z_][^\]]*\]', '', value)
        # Runtime-only UI template variables are absent from the statically rendered catalogue.
        value = re.sub(r'\{[^}]*\}', '', value)
        value = re.sub(r'<[^>]+>', '', value)
        value = re.sub(r'[ \t]+', ' ', value)
        value = re.sub(r'(?<=[\u4e00-\u9fff])[ \t]+(?=[\u4e00-\u9fff])', '', value)
        value = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', value)
        return value.strip()

    def name(self, type_name: str | None):
        if not type_name: return ''
        for category, (table, key, _) in CATEGORIES.items():
            if type_name.startswith({'civilizations': 'CIVILIZATION_', 'leaders': 'LEADER_', 'units': 'UNIT_', 'buildings': 'BUILDING_', 'wonders': 'BUILDING_', 'districts': 'DISTRICT_', 'technologies': 'TECH_', 'civics': 'CIVIC_', 'resources': 'RESOURCE_', 'concepts': 'PAGE_'}[category]):
                row = self.rows(table, **{key: type_name})
                if row:
                    value = self.clean(row[0].get('Name', ''))
                    if value: return value
        return self.clean('LOC_' + type_name + '_NAME')

    def history(self, section: str, type_name: str):
        prefix = f'LOC_PEDIA_{section.upper()}_PAGE_{type_name}_CHAPTER_HISTORY_PARA_'
        paragraphs = [(int(tag[len(prefix):]), self.clean(value)) for tag, value in self.text['zh_Hans_CN'].items() if tag.startswith(prefix) and tag[len(prefix):].isdigit()]
        return [value for _, value in sorted(paragraphs) if value]

    def trait_descriptions(self, table: str, owner_key: str, type_name: str):
        descriptions = []
        for relation in self.rows(table, **{owner_key: type_name}):
            trait = self.rows('Traits', TraitType=relation['TraitType'])
            if not trait: continue
            title, body = self.clean(trait[0].get('Name', '')), self.clean(trait[0].get('Description', ''))
            if body: descriptions.append((title + '：' if title else '') + body)
        return descriptions

    def stat(self, stats: list, label: str, value, suffix='', allow_zero=False):
        if value is None or value == '' or (not allow_zero and str(value) in ('0', '0.0')): return
        formatted = str(value) + suffix
        existing = next((item for item in stats if item['label'] == label), None)
        if existing:
            if formatted not in existing['value'].split('；'): existing['value'] += '；' + formatted
        else:
            stats.append({'label': label, 'value': formatted})

    def prerequisites(self, row: dict):
        requirements = []
        for key, label in (('PrereqTech', '科技'), ('PrereqCivic', '市政'), ('PrereqDistrict', '区域')):
            if row.get(key): requirements.append(label + '「' + self.name(row[key]) + '」')
        return requirements

    def build(self):
        entries, source_entries = [], []
        purchase_rule_file = self.record_file(self.game / 'Base/Assets/UI/Civilopedia/CivilopediaPage_Unit.lua')
        global_parameters = {row['Name']: float(row['Value']) for row in self.rows('GlobalParameters') if re.fullmatch(r'-?\d+(?:\.\d+)?', str(row.get('Value', '')))}
        gold_multiplier = global_parameters['GOLD_PURCHASE_MULTIPLIER']
        other_yield_multiplier = global_parameters['GOLD_EQUIVALENT_OTHER_YIELDS']
        full_civs = {row['CivilizationType'] for row in self.rows('Civilizations') if row['StartingCivilizationLevelType'] == 'CIVILIZATION_LEVEL_FULL_CIV'}
        playable_leaders = {row['LeaderType'] for row in self.rows('CivilizationLeaders') if row['CivilizationType'] in full_civs}
        for category, (table, key, category_label) in CATEGORIES.items():
            for row in self.rows(table):
                type_name = row[key]
                if category == 'civilizations' and type_name not in full_civs: continue
                if category == 'leaders' and type_name not in playable_leaders: continue
                if category in ('buildings', 'wonders') and (bool(row.get('IsWonder')) != (category == 'wonders') or row.get('InternalOnly')): continue
                if category == 'districts' and row.get('InternalOnly'): continue
                if category == 'units' and row.get('TraitType') == 'TRAIT_BARBARIAN': continue
                if category == 'resources' and (type_name.startswith('RESOURCE_ARTIFACT') or type_name == 'RESOURCE_ANTIQUITY_SITE' or type_name == 'RESOURCE_SHIPWRECK'): continue
                if category == 'concepts' and (row.get('SectionId') != 'CONCEPTS' or type_name == 'INTRO'): continue
                title = self.clean(row.get('Name', ''))
                if not title: continue
                english = self.clean(row.get('Name', ''), 'en_US')
                tags = [category_label]
                stats, notes = [], []
                body = self.clean(row.get('Description', ''))
                derived_description_tag = 'LOC_' + type_name + '_DESCRIPTION'
                if not body and derived_description_tag in self.text['zh_Hans_CN']:
                    body = self.clean(derived_description_tag)
                requirements = self.prerequisites(row)
                acquisition = '；'.join(requirements)
                history_section = category.upper()
                history = self.history(history_section, type_name)
                if category in ('civilizations', 'leaders'):
                    owner_key, relation = ('CivilizationType', 'CivilizationTraits') if category == 'civilizations' else ('LeaderType', 'LeaderTraits')
                    traits = self.trait_descriptions(relation, owner_key, type_name)
                    body = '\n\n'.join(traits) or (history[0] if history else body)
                    if category == 'civilizations':
                        leaders = [self.name(item['LeaderType']) for item in self.rows('CivilizationLeaders', CivilizationType=type_name)]
                        self.stat(stats, '可选领袖', '、'.join(dict.fromkeys(filter(None, leaders))))
                        uniques = []
                        trait_types = {item['TraitType'] for item in self.rows('CivilizationTraits', CivilizationType=type_name)}
                        for unique_table, unique_key in (('Units', 'UnitType'), ('Buildings', 'BuildingType'), ('Districts', 'DistrictType'), ('Improvements', 'ImprovementType')):
                            for unique in self.rows(unique_table):
                                if unique.get('TraitType') in trait_types: uniques.append(self.clean(unique.get('Name', '')))
                        self.stat(stats, '特色内容', '、'.join(filter(None, uniques)))
                        acquisition = '创建常规对局时选择此文明及其可用领袖。具体可选内容取决于已安装并启用的官方 DLC。'
                    else:
                        civs = [self.name(item['CivilizationType']) for item in self.rows('CivilizationLeaders', LeaderType=type_name)]
                        self.stat(stats, '领导文明', '、'.join(dict.fromkeys(filter(None, civs))))
                        tags.extend(dict.fromkeys(filter(None, civs)))
                        for relation_row in self.rows('HistoricalAgendas', LeaderType=type_name):
                            agenda = self.rows('Agendas', AgendaType=relation_row['AgendaType'])
                            if agenda:
                                agenda_name, agenda_desc = self.clean(agenda[0].get('Name', '')), self.clean(agenda[0].get('Description', ''))
                                self.stat(stats, '领袖议程', agenda_name)
                                if agenda_desc: notes.append('议程：' + agenda_desc)
                        acquisition = '创建常规对局时选择此领袖及其对应文明。具体可选内容取决于已安装并启用的官方 DLC。'
                elif category == 'units':
                    for field, label in (('Cost', '基础生产力成本'), ('BaseMoves', '移动力'), ('Combat', '近战战斗力'), ('RangedCombat', '远程战斗力'), ('Bombard', '轰击战斗力'), ('Range', '射程'), ('Maintenance', '每回合维护金币'), ('BuildCharges', '建造次数'), ('SpreadCharges', '传播次数'), ('ReligiousStrength', '宗教战斗力'), ('BaseSightRange', '视野')):
                        if field == 'Cost' and (row.get('MustPurchase') or not row.get('CanTrain', 1)): continue
                        self.stat(stats, label, row.get(field))
                    if row.get('PurchaseYield') and row.get('CanTrain', 1):
                        purchase_yield = self.clean('LOC_' + row['PurchaseYield'] + '_NAME').removesuffix('值')
                        purchase_cost = row['Cost'] * other_yield_multiplier * (gold_multiplier if row['PurchaseYield'] == 'YIELD_GOLD' else 1)
                        self.stat(stats, '基础' + purchase_yield + '购买成本', f'{purchase_cost:g}')
                    unit_building_prereqs = [self.name(item['PrereqBuilding']) for item in self.rows('Unit_BuildingPrereqs', Unit=type_name)]
                    if unit_building_prereqs:
                        requirements.append('城市建有「' + ' / '.join(filter(None, unit_building_prereqs)) + '」' + ('之一' if len(unit_building_prereqs) > 1 else ''))
                        self.stat(stats, '前置建筑', ' / '.join(filter(None, unit_building_prereqs)))
                        acquisition = '；'.join(requirements)
                    if row.get('CostProgressionModel') == 'COST_PROGRESSION_PREVIOUS_COPIES':
                        notes.append('该单位采用随已生产或购买数量增加的成本模型；此处仅显示初始基础成本，后续招募费用会提高。')
                    if row.get('TrackReligion'): requirements.append('购买城市须信仰一个宗教')
                    if row.get('RequiresInquisition'): requirements.append('已用使徒发起宗教审讯')
                    acquisition = '；'.join(requirements)
                    domain = {'DOMAIN_LAND': '陆地单位', 'DOMAIN_SEA': '海军单位', 'DOMAIN_AIR': '空中单位'}.get(row.get('Domain'))
                    if domain: tags.append(domain)
                    for relation in self.rows('UnitReplaces', CivUniqueUnitType=type_name): self.stat(stats, '替代单位', self.name(relation['ReplacesUnitType']))
                    for relation in self.rows('UnitUpgrades', Unit=type_name): self.stat(stats, '可升级为', self.name(relation['UpgradeUnit']))
                    if row.get('StrategicResource'):
                        self.stat(stats, '战略资源', self.name(row['StrategicResource']))
                    for resource_cost in self.rows('Units_XP2', UnitType=type_name):
                        self.stat(stats, '资源储备成本', resource_cost.get('ResourceCost'))
                        if resource_cost.get('ResourceMaintenanceType'): self.stat(stats, '每回合消耗资源', self.name(resource_cost['ResourceMaintenanceType']) + ' ' + str(resource_cost['ResourceMaintenanceAmount']))
                    if not row.get('CanTrain', 1):
                        acquisition = '通过对应类型的伟人点数参与招募，也可按规则使用金币或信仰赞助；伟人单位不能在城市直接生产。'
                        tags.append('伟人单位')
                        if type_name == 'UNIT_COMANDANTE_GENERAL':
                            acquisition = '西蒙·玻利瓦尔的「荣耀之战」领袖能力在游戏进入新时代后赠予1名；总指挥通过该能力获得，不能在城市直接生产。'
                    elif row.get('MustPurchase'): acquisition = ('需要' + acquisition + '；' if acquisition else '') + '须使用' + self.clean('LOC_' + row.get('PurchaseYield', 'YIELD_GOLD') + '_NAME') + '购买，不能直接生产。'
                    else: acquisition = ('需要' + acquisition + '后' if acquisition else '常规对局中') + '在城市生产或按规则购买。'
                    if row.get('TraitType'):
                        owner_relations = self.rows('CivilizationTraits', TraitType=row['TraitType'])
                        owners = [self.name(item['CivilizationType']) for item in owner_relations]
                        owners += [self.name(item['LeaderType']) for item in self.rows('LeaderTraits', TraitType=row['TraitType'])]
                        if owners: acquisition += '特色单位，限定：' + '、'.join(dict.fromkeys(filter(None, owners))) + '。'; tags.append('特色单位')
                        for owner in owner_relations:
                            civilization = self.rows('Civilizations', CivilizationType=owner['CivilizationType'])
                            if civilization and civilization[0]['StartingCivilizationLevelType'] == 'CIVILIZATION_LEVEL_CITY_STATE':
                                acquisition = '成为' + self.name(owner['CivilizationType']) + '城邦的宗主国后，使用信仰值购买此城邦特色单位。'
                                tags.append('城邦特色')
                elif category in ('buildings', 'wonders', 'districts'):
                    for field, label in (('Cost', '基础生产力成本'), ('Maintenance', '每回合维护金币'), ('Housing', '住房'), ('Entertainment', '宜居度'), ('CitizenSlots', '专家槽位'), ('OuterDefenseHitPoints', '外部防御生命值'), ('OuterDefenseStrength', '外部防御力')):
                        if field == 'Cost' and (row.get('Capital') or row.get('CityCenter')): continue
                        self.stat(stats, label, row.get(field), allow_zero=field == 'Cost')
                    relation_table, foreign_key = ('District_YieldChanges', 'DistrictType') if category == 'districts' else ('Building_YieldChanges', 'BuildingType')
                    for output in self.rows(relation_table, **{foreign_key: type_name}): self.stat(stats, '基础产出', self.clean('LOC_' + output['YieldType'] + '_NAME') + ' +' + str(output['YieldChange']))
                    points_table = 'District_GreatPersonPoints' if category == 'districts' else 'Building_GreatPersonPoints'
                    for points in self.rows(points_table, **{foreign_key: type_name}):
                        person = self.rows('GreatPersonClasses', GreatPersonClassType=points['GreatPersonClassType'])
                        person_name = self.clean(person[0].get('Name', '')) if person else ''
                        self.stat(stats, '每回合伟人点数', person_name + ' +' + str(points['PointsPerTurn']))
                    if category == 'buildings':
                        prereqs = [self.name(item['PrereqBuilding']) for item in self.rows('BuildingPrereqs', Building=type_name)]
                        if prereqs: requirements.append('前置建筑「' + ' / '.join(filter(None, prereqs)) + '」')
                        acquisition = ('需要' + '；'.join(requirements) + '后' if requirements else '常规对局中') + '在对应城市或区域建造。'
                        if row.get('Capital'): acquisition = '作为首都的宫殿自动提供；无需手动生产。首都改变时按游戏规则转移。'
                    elif category == 'wonders': acquisition = ('需要' + acquisition + '。' if acquisition else '') + '满足地块与邻接要求后建造；每种世界奇观在同一对局中只能建成一次。'
                    else: acquisition = ('需要' + acquisition + '后' if acquisition else '常规对局中') + '在合法地块上放置并建造；实际生产力成本会随游戏进度变化。'
                    if row.get('CityCenter'):
                        acquisition = '建立城市时自动生成，作为城市中心存在。'
                        self.stat(stats, '建立方式', '建立城市时自动生成')
                    if row.get('TraitType'):
                        owners = [self.name(item['CivilizationType']) for item in self.rows('CivilizationTraits', TraitType=row['TraitType'])]
                        if owners: acquisition += '文明特色内容，限定：' + '、'.join(filter(None, owners)) + '。'; tags.append('文明特色')
                    if not body:
                        outputs = [item['value'] for item in stats if item['label'] in ('基础产出', '每回合伟人点数')]
                        body = (self.name(row.get('PrereqDistrict')) + '中的' if row.get('PrereqDistrict') else '') + category_label + '。'
                        if outputs: body += '提供' + '；'.join(outputs) + '。'
                        if history: body += '\n\n' + history[0]
                elif category in ('technologies', 'civics'):
                    self.stat(stats, '所需' + ('科技值' if category == 'technologies' else '文化值'), row.get('Cost'))
                    era = self.clean('LOC_' + row.get('EraType', '') + '_NAME')
                    self.stat(stats, '时代', era)
                    if era: tags.append(era)
                    prereq_table, prereq_field = ('TechnologyPrereqs', 'PrereqTech') if category == 'technologies' else ('CivicPrereqs', 'PrereqCivic')
                    prereq_owner = 'Technology' if category == 'technologies' else 'Civic'
                    predecessors = [self.name(item[prereq_field]) for item in self.rows(prereq_table, **{prereq_owner: type_name})]
                    acquisition = ('先完成' + '、'.join('「' + item + '」' for item in predecessors if item) + '，再' if predecessors else '') + ('研究此科技。' if category == 'technologies' else '发展此市政。')
                    unlocks = []
                    for unlock_table in ('Units', 'Buildings', 'Districts', 'Improvements', 'Policies', 'Governments', 'Projects'):
                        for unlock in self.rows(unlock_table, **{prereq_field: type_name}):
                            if unlock.get('InternalOnly'): continue
                            unlocked_name = self.clean(unlock.get('Name', unlock.get('ShortName', '')))
                            if unlocked_name: unlocks.append(unlocked_name)
                    if category == 'technologies':
                        for route_unlock in self.rows('Routes_XP2', PrereqTech=type_name):
                            route = self.rows('Routes', RouteType=route_unlock['RouteType'])
                            if route: unlocks.append(self.clean(route[0]['Name']))
                    if unlocks: self.stat(stats, '解锁内容', '、'.join(dict.fromkeys(unlocks)))
                    for boost in self.rows('Boosts', **{key: type_name}):
                        trigger = self.clean(boost.get('TriggerDescription', ''))
                        if trigger:
                            self.stat(stats, '尤里卡条件' if category == 'technologies' else '鼓舞条件', trigger)
                            self.stat(stats, '尤里卡加速比例' if category == 'technologies' else '鼓舞加速比例', boost.get('Boost'), '%')
                            detail = self.clean(boost.get('TriggerLongDescription', ''))
                            if re.search(r'[\u4e00-\u9fff]', detail): notes.append(('尤里卡' if category == 'technologies' else '鼓舞') + '：' + detail)
                    unlock_description = ('研究完成后' if category == 'technologies' else '发展完成后') + ('解锁' + '、'.join(dict.fromkeys(unlocks)) + '。' if unlocks else '推进文明在科技树上的发展。' if category == 'technologies' else '推进文明在市政树上的发展。')
                    body = (body + '\n\n' if body else '') + unlock_description
                    if history: body += '\n\n' + history[0]
                elif category == 'resources':
                    resource_class = {'RESOURCECLASS_BONUS': '加成资源', 'RESOURCECLASS_LUXURY': '奢侈品资源', 'RESOURCECLASS_STRATEGIC': '战略资源'}.get(row.get('ResourceClassType'), '资源')
                    tags.append(resource_class)
                    self.stat(stats, '资源类型', resource_class)
                    if row.get('PrereqTech'): self.stat(stats, '显示所需科技', self.name(row['PrereqTech']))
                    if row.get('Happiness'): self.stat(stats, '可分配宜居度', row['Happiness'])
                    for consumption in self.rows('Resource_Consumption', ResourceType=type_name):
                        self.stat(stats, '改良后每回合积累', consumption.get('ImprovedExtractionRate'))
                        self.stat(stats, '基础储备上限', consumption.get('StockpileCap'))
                        self.stat(stats, '每单位资源供电量', consumption.get('PowerProvided'))
                    for output in self.rows('Resource_YieldChanges', ResourceType=type_name): self.stat(stats, '地块基础产出', self.clean('LOC_' + output['YieldType'] + '_NAME') + ' +' + str(output['YieldChange']))
                    improvements = []
                    for relation in self.rows('Improvement_ValidResources', ResourceType=type_name):
                        improved = self.rows('Improvements', ImprovementType=relation['ImprovementType'])
                        if improved: improvements.append(self.clean(improved[0]['Name']))
                    if improvements: self.stat(stats, '开发设施', '、'.join(dict.fromkeys(filter(None, improvements))))
                    acquisition = ('完成科技「' + self.name(row['PrereqTech']) + '」后可发现。' if row.get('PrereqTech') else '可在对应地形的地图地块上发现。') + ('使用建造者修建' + '、'.join(dict.fromkeys(improvements)) + '开发此资源。' if improvements else '在所属城市领土内按游戏规则利用。')
                    if type_name in ('RESOURCE_CINNAMON', 'RESOURCE_CLOVES'):
                        acquisition = '成为桑给巴尔城邦的宗主国后获得；该特殊奢侈品不会自然生成在地图地块上。'
                        tags.append('城邦特供')
                    elif row.get('Frequency') == 0:
                        people = []
                        for argument in self.rows('ModifierArguments', Value=type_name):
                            for relation in self.rows('GreatPersonIndividualActionModifiers', ModifierId=argument['ModifierId']):
                                person = self.rows('GreatPersonIndividuals', GreatPersonIndividualType=relation['GreatPersonIndividualType'])
                                if person: people.append(self.clean(person[0]['Name']))
                        if people:
                            acquisition = '招募并激活大商人「' + ' / '.join(dict.fromkeys(people)) + '」获得；该特殊奢侈品不会自然生成在地图地块上。'
                            self.stat(stats, '对应大商人', '、'.join(dict.fromkeys(people)))
                            tags.append('伟人特供')
                    body = body or resource_class + '。' + ('改良后可由所属文明利用。' if improvements else '')
                    if history: body += '\n\n' + history[0]
                elif category == 'concepts':
                    chapter_prefix = f'LOC_PEDIA_CONCEPTS_PAGE_{type_name}_CHAPTER_'
                    chapter_orders = {'CONTENT': 0}
                    chapter_orders.update({item['ChapterId']: item['SortIndex'] for item in self.rows('CivilopediaPageLayoutChapters', PageLayoutId=row.get('PageLayoutId', 'Simple'))})
                    paragraphs = []
                    for tag, value in self.text['zh_Hans_CN'].items():
                        if not tag.startswith(chapter_prefix): continue
                        match = re.fullmatch(r'(.+)_PARA_(\d+)', tag[len(chapter_prefix):])
                        if match: paragraphs.append((chapter_orders.get(match.group(1), 999), int(match.group(2)), match.group(1), self.clean(value)))
                    chunks, current_chapter = [], None
                    for _, _, chapter, paragraph in sorted(paragraphs):
                        if not paragraph: continue
                        if chapter != current_chapter and chapter != 'CONTENT':
                            chapter_title = self.clean(chapter_prefix + chapter + '_TITLE')
                            if chapter_title: chunks.append(chapter_title)
                        chunks.append(paragraph)
                        current_chapter = chapter
                    body = '\n\n'.join(chunks)
                    if not body: continue
                    group = row.get('PageGroupId', '')
                    localized_group = self.rows('CivilopediaPageGroups', SectionId='CONCEPTS', PageGroupId=group)
                    group_name = self.clean(localized_group[0].get('Name', '')) if localized_group else GROUPS.get(group, group)
                    if group_name: tags.append(group_name)
                    if title in ('介绍', '简介') and group_name: title = group_name + '介绍'
                    acquisition = '在常规对局的相应系统中查看与使用；本条介绍来自游戏内文明百科。'
                    self.stat(stats, '百科章节', group_name)
                    type_name = 'CONCEPT_' + type_name
                if not body: body = '\n\n'.join(history[:2])
                if not body: continue
                if history and category not in ('concepts', 'technologies', 'civics'):
                    notes.extend('历史背景：' + paragraph for paragraph in history[:2] if paragraph not in body)
                if category not in ('concepts', 'civilizations', 'leaders', 'resources'):
                    notes.append('属性为标准速度下的规则基础值；实际费用、产出与战斗数值会受到时代、政策、文明能力及其他游戏效果影响。')
                page_type = type_name.removeprefix('CONCEPT_')
                url = f'https://www.civilopedia.net/zh-CN/gathering-storm/{category}/{page_type.lower()}/'
                icon_name = 'ICON_CIVILOPEDIA_CONCEPTS' if category == 'concepts' else 'ICON_' + type_name
                entry = {'id': 'civ6-' + type_name, 'category': category, 'name': title, 'englishName': english,
                         'description': body, 'image': f'/images/civilization-vi/{type_name}.png',
                         'tags': list(dict.fromkeys(filter(None, tags))), 'acquisition': acquisition,
                         'stats': stats, 'notes': list(dict.fromkeys(filter(None, notes))),
                         'sources': [{'label': '文明百科 · 风云变幻（对应条目）', 'url': url}]}
                entries.append(entry)
                source_files = set(self.provenance[(table, str(row[key]))])
                if category == 'units' and row.get('PurchaseYield'): source_files.add(purchase_rule_file)
                for field in ('Name', 'Description'):
                    if row.get(field) and ('zh_Hans_CN', row[field]) in self.text_sources: source_files.add(self.text_sources[('zh_Hans_CN', row[field])])
                if ('zh_Hans_CN', derived_description_tag) in self.text_sources: source_files.add(self.text_sources[('zh_Hans_CN', derived_description_tag)])
                source_entries.append({'id': entry['id'], 'category': category, 'sourceType': type_name, 'iconName': icon_name, 'sourceFiles': sorted(source_files), 'sourceUrl': url})
        return entries, source_entries


def main():
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=Path, default=DEFAULT_GAME)
    args = parser.parse_args()
    extractor = Extractor(args.game)
    extractor.load()
    entries, entry_sources = extractor.build()
    image_map = ROOT / 'public/images/civilization-vi/image-map.json'
    if image_map.exists():
        images = json.loads(image_map.read_text(encoding='utf-8'))
        images = images.get('images', images) if isinstance(images, dict) else {item['sourceType']: item for item in images}
        for entry, source in zip(entries, entry_sources):
            image = images.get(source['sourceType'])
            if isinstance(image, str): entry['image'] = image
            elif isinstance(image, dict): entry['image'] = image.get('image', image.get('path', entry['image']))
    save(ROOT / 'app/data/civilization-vi.entries.json', entries)
    counts = dict(Counter(entry['category'] for entry in entries))
    player_text = '\n'.join('\n'.join([entry['name'], entry['description'], entry.get('acquisition', ''),
                                       *entry['notes'], *entry['tags'],
                                       *(stat['label'] + stat['value'] for stat in entry['stats'])]) for entry in entries)
    source = {'game': 'Civilization VI', 'ruleset': 'RULESET_EXPANSION_2', 'rulesetName': '风云变幻',
              'generatedAt': datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
              'localGamePath': str(args.game), 'entryCount': len(entries), 'categoryCounts': counts,
              'unresolvedTokens': sorted(set(re.findall(r'LOC_[A-Z0-9_]+|\[ICON_[^\]]+\]|\[NEWLINE\]|\{[^}]+\}', player_text))),
              'missingOptionalLocalizationKeys': sorted(extractor.missing_localization),
              'resolvedLocalizationAliases': extractor.localization_aliases,
              'extractionWarnings': list(dict.fromkeys(extractor.warnings)),
              'files': [{'path': path, 'sha256': sha} for path, sha in sorted(extractor.files.items())],
              'entries': entry_sources}
    save(ROOT / 'app/data/civilization-vi.source.json', source)
    print(json.dumps({'entryCount': len(entries), 'categoryCounts': counts, 'unresolvedTokens': source['unresolvedTokens'], 'missingOptionalLocalizationKeys': source['missingOptionalLocalizationKeys'], 'warningCount': len(source['extractionWarnings'])}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
