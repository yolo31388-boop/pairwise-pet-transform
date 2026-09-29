"""宠物合体与变身系统"""
import random
from dataclasses import dataclass, field

# bug1: 合体条件限制
MIN_FUSION_LEVEL = 10
MIN_FUSION_INTIMACY = 50
# 相克属性表：这些组合不能合体
INCOMPATIBLE_ELEMENTS = {
    frozenset(("fire", "water")),
    frozenset(("earth", "wind")),
}

# bug2: 属性公式：主宠70% + 副宠30%，再乘衰减系数
MAIN_PET_RATIO = 0.7
SUB_PET_RATIO = 0.3
STAT_DECAY = 0.9

# bug3: 合体技能按主副宠属性组合决定
FUSION_SKILLS = {
    frozenset(("fire", "fire")): "inferno_burst",
    frozenset(("water", "water")): "tidal_wave",
    frozenset(("earth", "earth")): "quake_strike",
    frozenset(("wind", "wind")): "cyclone_slash",
    frozenset(("fire", "water")): "steam_blast",
    frozenset(("fire", "earth")): "magma_eruption",
    frozenset(("fire", "wind")): "flame_vortex",
    frozenset(("water", "earth")): "mud_shot",
    frozenset(("water", "wind")): "ice_storm",
    frozenset(("earth", "wind")): "sandstorm",
}

# bug4: 变身时间限制（秒）
FUSION_DURATION = 60.0

# bug5: 变身形态概率表 + 保底次数
FORM_TABLE = {"fire": 0.3, "water": 0.3, "earth": 0.2, "wind": 0.2}
FORM_PITY_THRESHOLD = 10  # 连续10次未出目标形态则必出

# bug6: 合体失败消耗材料比例
FAILURE_MATERIAL_COST = 0.5

# bug7: 合体冷却（秒）
FUSION_COOLDOWN = 3600.0

# bug8: 变身能量条
MAX_ENERGY = 100.0
SKILL_ENERGY_COSTS = {"ultimate": 40.0, "normal": 15.0}
DEFAULT_ENERGY_COST = 20.0

# bug9: 继承技能上限
INHERITED_SKILLS_LIMIT = 3


@dataclass
class Pet:
    pid: str
    name: str
    level: int = 1
    element: str = "fire"
    atk: int = 100
    skills: list = field(default_factory=list)
    intimacy: int = 0


@dataclass
class FusedPet:
    """合体变身状态：有剩余时间和能量条，耗尽即解除。"""
    main: Pet
    sub: Pet
    atk: int
    skill: str
    form: str
    skills: list
    remaining_time: float = FUSION_DURATION
    energy: float = MAX_ENERGY

    @property
    def active(self) -> bool:
        return self.remaining_time > 0 and self.energy > 0

    def tick(self, seconds: float) -> bool:
        """时间流逝，时间耗尽变回主宠。"""
        self.remaining_time = max(0.0, self.remaining_time - seconds)
        return self.active

    def cast_skill(self, skill: str = "normal") -> bool:
        """放技能消耗能量，能量耗尽强制解除变身。"""
        cost = SKILL_ENERGY_COSTS.get(skill, DEFAULT_ENERGY_COST)
        if not self.active or self.energy < cost:
            return False
        self.energy -= cost
        return self.active


class FusionSystem:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        # bug5: 保底计数器，记录每个目标形态连续未中的次数
        self.form_pity = {}
        # bug7: 上次合体时间戳（秒），None 表示从未合体
        self._last_fusion_time = None

    # bug1: 合体有条件限制：属性相容、等级达标、亲密度足够
    def can_fuse(self, p1: Pet, p2: Pet) -> bool:
        if frozenset((p1.element, p2.element)) in INCOMPATIBLE_ELEMENTS:
            return False
        if p1.level < MIN_FUSION_LEVEL or p2.level < MIN_FUSION_LEVEL:
            return False
        if p1.intimacy < MIN_FUSION_INTIMACY or p2.intimacy < MIN_FUSION_INTIMACY:
            return False
        return True

    # bug2: 属性按公式计算（主70% + 副30%，乘衰减系数），不是简单相加
    def calculate_fused_stats(self, p1: Pet, p2: Pet) -> dict:
        atk = (p1.atk * MAIN_PET_RATIO + p2.atk * SUB_PET_RATIO) * STAT_DECAY
        return {"atk": int(atk)}

    # bug3: 合体技能按主副宠属性组合决定
    def get_fusion_skill(self, p1_element: str, p2_element: str) -> str:
        return FUSION_SKILLS.get(
            frozenset((p1_element, p2_element)), "fusion_attack"
        )

    # bug4: 变身有时间限制，默认60秒
    def get_fusion_duration(self) -> float:
        return FUSION_DURATION

    # bug5: 形态按概率表抽取，连续 N 次未出目标形态则保底必出
    def get_form_roll(self, target_form: str) -> tuple[str, bool]:
        count = self.form_pity.get(target_form, 0)
        if count + 1 >= FORM_PITY_THRESHOLD:
            self.form_pity[target_form] = 0
            return target_form, True
        forms = list(FORM_TABLE)
        weights = [FORM_TABLE[f] for f in forms]
        form = self.rng.choices(forms, weights=weights, k=1)[0]
        if form == target_form:
            self.form_pity[target_form] = 0
            return form, True
        self.form_pity[target_form] = count + 1
        return form, False

    # bug6: 合体失败消耗材料（默认50%），有失败惩罚
    def fusion_failure_cost(self) -> dict:
        return {"material_cost": FAILURE_MATERIAL_COST}

    # bug7: 合体有冷却时间（默认1小时）
    def get_fusion_cooldown(self) -> float:
        return FUSION_COOLDOWN

    def check_cooldown(self, now: float) -> bool:
        """当前时刻是否可以合体（冷却是否结束）。"""
        if self._last_fusion_time is None:
            return True
        return now - self._last_fusion_time >= FUSION_COOLDOWN

    # bug8: 放合体技能消耗能量
    def get_energy_cost(self, skill: str) -> float:
        return SKILL_ENERGY_COSTS.get(skill, DEFAULT_ENERGY_COST)

    # bug9: 继承有选择机制，最多继承3个技能
    def get_inherited_skills_limit(self) -> int:
        return INHERITED_SKILLS_LIMIT

    def select_inherited_skills(self, p1: Pet, p2: Pet) -> list:
        """从两只宠物技能中选择继承，最多 INHERITED_SKILLS_LIMIT 个。"""
        combined = list(dict.fromkeys(p1.skills + p2.skills))
        return combined[: INHERITED_SKILLS_LIMIT]

    def fuse(self, p1: Pet, p2: Pet, target_form: str = None,
             now: float = 0.0) -> FusedPet | None:
        """执行合体：校验条件与冷却，成功后进入限时变身状态。"""
        if not self.can_fuse(p1, p2) or not self.check_cooldown(now):
            return None
        self._last_fusion_time = now
        form, _ = self.get_form_roll(target_form or p1.element)
        stats = self.calculate_fused_stats(p1, p2)
        return FusedPet(
            main=p1,
            sub=p2,
            atk=stats["atk"],
            skill=self.get_fusion_skill(p1.element, p2.element),
            form=form,
            skills=self.select_inherited_skills(p1, p2),
            remaining_time=self.get_fusion_duration(),
            energy=MAX_ENERGY,
        )
