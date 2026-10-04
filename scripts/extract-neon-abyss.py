# @author Brave
# @date 2026-10-04T17:28:49+08:00
# @description 只读解析 PC 版霓虹深渊配置，按实际中文与图标引用生成百科。
# 依赖安装：python -m venv .tools/unity；.tools/unity/Scripts/pip install UnityPy TypeTreeGeneratorAPI
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import UnityPy
from UnityPy.classes.PPtr import PPtr
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from UnityPy.helpers.TypeTreeNode import TypeTreeNode

ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = ROOT / "public/images/neon-abyss"
DATA_DIR = ROOT / "app/data"
TIME_ZONE = timezone(timedelta(hours=8))


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def raw_name(obj) -> str:
    raw = obj.get_raw_data()
    size = struct.unpack_from("<I", raw, 28)[0]
    return raw[32:32 + size].decode("utf-8")


def read_config(obj) -> dict:
    try:
        return obj.read_typetree()
    except Exception:
        original = obj._get_typetree_node()
        # 旧资源中的附加字段与新版程序集不完全一致，公共 PowerUp 基类字段稳定。
        children = original.m_Children
        if not any(node.m_Name == "Name" for node in children[:22]):
            raise
        base = TypeTreeNode(original.m_Level, original.m_Type, original.m_Name,
                            original.m_ByteSize, original.m_Version, children[:22],
                            m_MetaFlag=original.m_MetaFlag)
        return obj.read_typetree(nodes=base, check_read=False)


def deref(obj, pointer: dict):
    return PPtr(**pointer, assetsfile=obj.assets_file).deref()


def read_localization(obj) -> dict[str, list[str]]:
    # I2 LanguageSource：mTerms 位于稳定头部后的 56 字节处。
    raw = obj.get_raw_data()
    offset = 56

    def integer() -> int:
        nonlocal offset
        value = struct.unpack_from("<I", raw, offset)[0]
        offset += 4
        return value

    def string() -> str:
        nonlocal offset
        size = integer()
        result = raw[offset:offset + size].decode("utf-8")
        offset = (offset + size + 3) // 4 * 4
        return result

    result = {}
    for _ in range(integer()):
        key = string()
        integer()
        string()
        languages = [string() for _ in range(integer())]
        flag_count = integer()
        offset = (offset + flag_count + 3) // 4 * 4
        [string() for _ in range(integer())]
        result[key] = languages
    return result


def clean(value: str) -> str:
    value = re.sub(r"<[^>]*>", "", value)
    return value.replace("{[k:Passive]}", "角色技能键").replace("{[k:Cancel]}", "取消键").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-dir", type=Path, default=Path("E:/SteamLibrary/steamapps/common/Neon Abyss"))
    args = parser.parse_args()
    game_data = args.game_dir / "NeonAbyss_Data"
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    generator = TypeTreeGenerator("2018.4.21f1")
    generator.load_local_dll_folder(str(game_data / "Managed"))
    paths = [*game_data.glob("*.assets"), *game_data.glob("*.resS"), game_data / "globalgamemanagers",
             *[game_data / "StreamingAssets" / name for name in ("props", "actor", "neonshared")]]
    environment = UnityPy.load(*[str(path) for path in paths])
    environment.typetree_generator = generator
    player_settings = next(obj for obj in environment.objects if obj.type.name == "PlayerSettings").read_typetree()
    game_version = player_settings.get("bundleVersion", "未知")
    steam_manifest = args.game_dir.parent.parent / "appmanifest_788100.acf"
    steam_build = "未知"
    if steam_manifest.is_file():
        match = re.search(r'"buildid"\s+"(\d+)"', steam_manifest.read_text(encoding="utf-8"))
        if match:
            steam_build = match.group(1)
    localization_obj = next(obj for obj in environment.objects if obj.type.name == "MonoBehaviour" and raw_name(obj) == "I2Languages")
    terms = read_localization(localization_obj)

    def localized(term: str, language: int = 2) -> str:
        values = terms.get(term, [])
        return clean(values[language] if len(values) > language else "")

    records = defaultdict(list)
    configurations = {}
    errors = []
    for obj in environment.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        name = raw_name(obj)
        if not name.startswith(("0_", "1_", "2_", "3_", "4_", "5_", "6_", "7_", "8_", "9_")):
            continue
        try:
            data = read_config(obj)
        except Exception as error:
            errors.append({"asset": obj.assets_file.name, "name": name, "reason": str(error)})
            continue
        configurations[(obj.assets_file.name, obj.path_id)] = (obj, data)
        if not {"sprite", "Name", "Description", "id"} <= data.keys():
            continue
        term = data["Name"].get("mTerm", "")
        if term in terms:
            records[term].append((obj, data))

    def read_pointer(obj, pointer: dict):
        target = deref(obj, pointer)
        key = (target.assets_file.name, target.path_id)
        if key not in configurations:
            configurations[key] = (target, read_config(target))
        return configurations[key]

    entries = []
    provenance = []
    skipped = []
    for term, alternatives in records.items():
        short_key = term.removeprefix("PuName/")
        if short_key.startswith("1_weapon_"):
            category = "weapons"
        elif short_key.startswith(("6_pet_", "6_guard_")):
            category = "pets"
        elif short_key.startswith(("3_item_", "4_item_", "5_", "7_item_badge_", "0_ticket_", "0_coin_", "0_gear_", "0_pickup_key_infinity")):
            category = "items"
        else:
            continue
        name = localized(term)
        if not name or set(name) <= {".", "…", " ", "·"}:
            skipped.append({"key": term, "reason": "空白或占位名称"})
            continue
        available = [(obj, data) for obj, data in alternatives if not data.get("isTestItem")]
        if not available:
            skipped.append({"key": term, "name": name, "reason": "所有配置均标记为 isTestItem"})
            continue
        available.sort(key=lambda pair: (not pair[0].assets_file.name.startswith("CAB-"), -len(pair[1])))
        selected = None
        for obj, data in available:
            try:
                sprite_obj = deref(obj, data["sprite"])
                if sprite_obj.type.name != "Sprite":
                    continue
                sprite = sprite_obj.read()
                image = sprite.image
                if not image.getbbox():
                    continue
                selected = (obj, data, sprite_obj, sprite, image)
                break
            except Exception:
                continue
        if not selected:
            skipped.append({"key": term, "name": name, "reason": "没有可解析的实际 Sprite 引用"})
            continue
        obj, data, sprite_obj, sprite, image = selected
        file_name = short_key + ".png"
        image.save(IMAGE_DIR / file_name)
        description = localized(data["Description"].get("mTerm", ""))
        if not description:
            skipped.append({"key": term, "name": name, "reason": "没有中文作用文本"})
            continue
        tags = []
        notes = []
        if category == "items":
            if short_key.startswith("0_ticket_"):
                tags.append("门票")
            elif short_key.startswith("0_coin_"):
                tags.append("特殊关卡")
            elif short_key.startswith("7_item_badge_"):
                tags.append("属性强化")
            else:
                item_group = {"01": "特殊效果", "02": "资源", "03": "受伤触发", "04": "战斗", "05": "子弹", "06": "近战", "07": "爆炸", "08": "蛋", "09": "宠物", "10": "跳跃", "11": "愤怒精灵"}
                tags.append(item_group.get(short_key.split("_")[1], "属性强化"))
        if category == "pets":
            tags.append("环绕物" if short_key.startswith("6_guard_") else "随行宠物")
            pointer = data.get("evolvesFrom", {})
            if pointer.get("m_PathID") and "mixthreebaby" not in short_key:
                try:
                    _, ancestor = read_pointer(obj, pointer)
                    ancestor_name = localized(ancestor.get("Name", {}).get("mTerm", ""))
                    if ancestor_name and ancestor_name != name:
                        notes.append(f"所属进化系列：{ancestor_name}。各形态具体获取见补充说明。")
                        tags.append("进化形态")
                except Exception:
                    pass
        if category == "weapons":
            tags.append("初始武器" if short_key.startswith("1_weapon_0_") else "深渊武器")
            skill_notes = set()
            for pointer in data.get("GunLevelSpecs", []):
                if not pointer.get("m_PathID"):
                    continue
                try:
                    spec_obj, spec = read_pointer(obj, pointer)
                    for skill_pointer in spec.get("SecskillPu", []):
                        _, skill = read_pointer(spec_obj, skill_pointer)
                        skill_name = localized(skill.get("Name", {}).get("mTerm", ""))
                        skill_description = localized(skill.get("Description", {}).get("mTerm", ""))
                        if skill_name and skill_description:
                            text = f"附带能力【{skill_name}】：{skill_description}"
                            if text not in skill_notes:
                                notes.append(text)
                                skill_notes.add(text)
                except Exception as error:
                    errors.append({"asset": obj.assets_file.name, "name": name, "reason": f"武器附带能力：{error}"})
            if skill_notes:
                tags.append("附带能力")
        entry = {"id": short_key, "category": category, "name": name,
                 "englishName": localized(term, 3).title(), "description": description,
                 "image": "/images/neon-abyss/" + file_name, "tags": tags}
        if notes:
            entry["notes"] = notes
        entries.append(entry)
        provenance.append({"id": short_key, "localizationKey": term,
                           "descriptionKey": data["Description"].get("mTerm"),
                           "configAsset": obj.assets_file.name, "configPathId": str(obj.path_id),
                           "gameIds": sorted({value["id"] for _, value in alternatives}),
                           "configNames": sorted({value["m_Name"] for _, value in alternatives}),
                           "spriteAsset": sprite_obj.assets_file.name,
                           "spritePathId": str(sprite_obj.path_id), "spriteName": sprite.m_Name,
                           "imageSize": list(image.size)})

    visuals = []
    for name, output in [("home_logo_cn", "game-logo.png"), ("home_bg_3x", "hero-background.png")]:
        candidates = [obj for obj in environment.objects if obj.type.name in {"Sprite", "Texture2D"} and obj.peek_name() == name]
        candidates.sort(key=lambda obj: obj.type.name != "Sprite")
        if candidates:
            try:
                sprite = candidates[0].read()
                sprite.image.save(IMAGE_DIR / output)
                visuals.append({"image": output, "asset": candidates[0].assets_file.name, "pathId": str(candidates[0].path_id), "spriteName": name})
            except Exception as error:
                errors.append({"name": name, "reason": f"横幅素材：{error}"})

    entries.sort(key=lambda entry: (entry["category"], entry["id"]))
    source = {"author": "Brave", "createdAt": datetime.now(TIME_ZONE).isoformat(timespec="seconds"),
              "game": "Neon Abyss", "platform": "Steam PC", "gameVersion": game_version, "steamBuildId": steam_build,
              "unityVersion": "2018.4.21f1", "textLanguage": "Chinese (Simplified) / zh-CN（语言索引 2）",
              "source": "用户提供的本地游戏只读资源；文字和图片按 ScriptableObject 引用对应",
              "counts": dict(Counter(entry["category"] for entry in entries)),
              "scope": "收录具有当前非测试配置、简体中文作用和实际图标引用的道具/武器/宠物；并未确认每项在所有游戏模式都可获取。进化形态名称不同者独立收录，相同显示词条合并。",
              "selectionRules": ["实际 Name / Description / sprite 引用优先于残留字符串", "使用 zh-CN 文本，避免废弃 Mainland China 翻译", "排除测试配置、空白名称、无图标、角色技能和装扮", "同一 Name 词条的多份资源及徽章变体只展示一项"],
              "limitations": ["未把残留本地化表等同于当前可获取内容", "游戏包仍包含旧配置；使用当前 zh-CN 和实际引用，但未运行游戏进行每项掉落实验", "武器射击图的内部计算未转成数值表；已提取64把武器的附带技能，剩余按原始游戏描述展示", "不同 PC 版本的道具合并、徽章替代和测试标记可能与旧版社区 Wiki 不同"],
              "localizationResource": {"asset": localization_obj.assets_file.name, "pathId": str(localization_obj.path_id), "sha256": hashlib.sha256(localization_obj.get_raw_data()).hexdigest()},
              "unusedLocalizationKeys": [key for key in terms if key.startswith("PuName/") and not key.endswith("D") and key not in records],
              "skipped": skipped, "parseIssues": errors, "entries": provenance, "visuals": visuals}
    save_json(DATA_DIR / "neon-abyss.entries.json", entries)
    save_json(DATA_DIR / "neon-abyss.source.json", source)
    print(json.dumps({"counts": source["counts"], "skipped": len(skipped), "parseIssues": len(errors), "entries": len(entries)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
