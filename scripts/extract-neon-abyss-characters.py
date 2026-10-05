# @author Brave
# @date 2026-10-04T21:48:01+08:00
# @description 只读提取 PC 霓虹深渊角色与异装的初始属性、技能文本及实际头像引用。
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("neon_extract", ROOT / "scripts/extract-neon-abyss.py")
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-dir', type=Path, default=Path('E:/SteamLibrary/steamapps/common/Neon Abyss'))
    args = parser.parse_args()
    game_data = args.game_dir / 'NeonAbyss_Data'
    generator = TypeTreeGenerator('2018.4.21f1')
    generator.load_local_dll_folder(str(game_data / 'Managed'))
    paths = [*game_data.glob('*.assets'), *game_data.glob('*.resS'), game_data / 'globalgamemanagers',
             game_data / 'StreamingAssets/actor', game_data / 'StreamingAssets/neonshared']
    environment = UnityPy.load(*map(str, paths))
    environment.typetree_generator = generator
    objects = {extract.raw_name(obj): obj for obj in environment.objects if obj.type.name == 'MonoBehaviour' and extract.raw_name(obj) in ('I2Languages', 'CharacterList', 'CharacterSkinList', 'New Unlock Character Config')}
    terms = extract.read_localization(objects['I2Languages'])

    def localized(value: dict, language: int = 2) -> str:
        texts = terms.get(value.get('mTerm', ''), [])
        return extract.clean(texts[language]) if len(texts) > language else ''

    unlocks = {value['Title']['mTerm']: value for value in objects['New Unlock Character Config'].read_typetree()['Values']}
    entries, provenance = [], []
    image_dir = ROOT / 'public/images/neon-abyss/characters'
    image_dir.mkdir(parents=True, exist_ok=True)
    for asset_name, field, is_alter in [('CharacterList', 'Values', False), ('CharacterSkinList', 'values', True)]:
        obj = objects[asset_name]
        for config in obj.read_typetree()[field]:
            term = config['Name']['mTerm']
            name = localized(config['Name'])
            if not name or term.endswith('_random'):
                continue
            key = term.rsplit('/', 1)[-1].removeprefix('player_') + ('-alter' if is_alter else '')
            print('Extracting', key, flush=True)
            skills, weapons = [], []
            skill_sources = []
            for pointer in [*config.get('needShowPowerUps', []), *config.get('PowerUps', [])]:
                target = extract.deref(obj, pointer)
                data = extract.read_config(target)
                skill_name = localized(data.get('Name', {}))
                description = localized(data.get('Description', {}))
                if not description or set(description) <= {'.', '…', ' '}:
                    continue
                skill_sources.append({'asset': target.assets_file.name, 'pathId': str(target.path_id), 'nameKey': data.get('Name', {}).get('mTerm'), 'descriptionKey': data.get('Description', {}).get('mTerm')})
                if 'weapon' in data.get('Name', {}).get('mTerm', '').lower():
                    weapons.append(skill_name)
                elif '7_' in data.get('Name', {}).get('mTerm', '') or pointer in config.get('needShowPowerUps', []):
                    skills.append(f'【{skill_name}】{description}' if skill_name else description)
            skills = list(dict.fromkeys(skills))
            image_obj = extract.deref(obj, config['Head'])
            image = image_obj.read().image
            image.save(image_dir / f'{key}.png')
            acquisition = '在酒吧的角色选择处使用。'
            if term in unlocks:
                unlock = unlocks[term]
                acquisition = f"在酒吧解锁树中解锁，角色节点消耗 {unlock['CostBossCoins']} 枚宝石；还需解锁通往该节点的前置节点。"
            if config.get('DLC_Character'):
                acquisition = '拥有 Lovable Rogues Pack DLC 后，在酒吧选择角色。'
            if term.endswith('_buro'):
                acquisition = 'PC 版 Muse Dash 联动角色，在酒吧的角色选择处使用。'
            if is_alter:
                acquisition = '拥有 Alter Ego DLC，并已解锁对应基础角色后，在酒吧切换异装。' + ('另需 Lovable Rogues Pack DLC。' if config.get('DLC_Character') else '')
            stats = [{'label': label, 'value': str(config[field]) + unit} for field, label, unit in (
                ('heart_count', '生命容器', ' 格'), ('shield_count', '护盾', ' 格'),
                ('key_count', '钥匙', ' 把'), ('bomb_count', '手雷', ' 枚'), ('coin_count', '金币', ' 枚'))]
            if weapons:
                stats.append({'label': '初始武器', 'value': '、'.join(dict.fromkeys(weapons))})
            intro = localized(config['Desc'])
            if not skills:
                skills = ['具备基础射击、跳跃与近战能力。']
            entry = {'id': f'character-{key}', 'category': 'characters', 'name': name + (' · 异装' if is_alter else ''),
                     'englishName': localized(config['Name'], 3).title() + (' · Alter Ego' if is_alter else ''),
                     'description': '\n'.join(skills), 'image': f'/images/neon-abyss/characters/{key}.png',
                     'tags': ['异装角色' if is_alter else '基础角色'] + (['DLC'] if is_alter or config.get('DLC_Character') else []),
                     'stats': stats, 'notes': [intro] if intro else [], 'acquisition': acquisition}
            if is_alter or config.get('DLC_Character'):
                entry['specialAcquisition'] = acquisition
            entries.append(entry)
            provenance.append({'id': entry['id'], 'listAsset': obj.assets_file.name, 'listName': asset_name,
                               'listPathId': str(obj.path_id), 'characterId': config['Id'], 'nameKey': term,
                               'config': config, 'skills': skill_sources, 'imageAsset': image_obj.assets_file.name, 'imagePathId': str(image_obj.path_id)})
    entries.sort(key=lambda entry: (entry['id'].endswith('-alter'), next(value['characterId'] for value in provenance if value['id'] == entry['id'])))
    extract.save_json(ROOT / 'app/data/neon-abyss.characters.json', entries)
    extract.save_json(ROOT / 'app/data/neon-abyss.characters.source.json', {'source': '本地 CharacterList / CharacterSkinList 实际配置与头像引用；不使用手游资料', 'entries': provenance})
    print(json.dumps({'characters': len(entries)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
