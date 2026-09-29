"""宠物合体与变身系统"""
from dataclasses import dataclass, field

@dataclass
class Pet:
    pid: str
    name: str
    level: int = 1
    element: str = "fire"
    atk: int = 100
    skills: list = field(default_factory=list)
    intimacy: int = 0

# 属性相容表：相克属性不能合体
INCOMPATIBLE_PAIRS = {frozenset(("fire", "water")), frozenset(("earth", "wind"))}

# 合体条件阈值
MIN_FUSION_LEVEL = 10
MIN_INTIMACY = 50

# 合体属性公式：主宠70% + 副宠30%，再乘衰减系数
MAIN_PET_RATIO = 0.7
SUB_PET_RATIO = 0.3
STAT_DECAY = 0.9

# 变身默认时长（秒）
FUSION_DURATION = 60.0

# 形态保底：连续 PITY_LIMIT 次未出目标形态则必出
PITY_LIMIT = 10
FORMS = ["fire", "water", "earth", "wind"]

# 合体失败惩罚：消耗50%材料
FAILURE_MATERIAL_RATIO = 0.5

# 合体冷却（秒）：默认1小时
FUSION_COOLDOWN = 3600.0

# 能量条
MAX_ENERGY = 100.0
SKILL_ENERGY_COSTS = {"ultimate": 40.0, "special": 25.0}
DEFAULT_ENERGY_COST = 10.0

# 技能继承上限
INHERITED_SKILLS_LIMIT = 3

# 属性组合 -> 合体技能
FUSION_SKILLS = {
    frozenset(("fire", "fire")): "blaze_fury",
    frozenset(("water", "water")): "tidal_wave",
    frozenset(("earth", "earth")): "stone_guard",
    frozenset(("wind", "wind")): "gale_dance",
    frozenset(("fire", "earth")): "magma_burst",
    frozenset(("fire", "wind")): "flame_cyclone",
    frozenset(("water", "earth")): "mud_slash",
    frozenset(("water", "wind")): "frost_storm",
}

class FusionSystem:
    def __init__(self, seed=42):
        import random
        self.rng = random.Random(seed)
        self.form_pity = {}          # 目标形态 -> 已连续未出次数
        self.energy = MAX_ENERGY
        self.last_fusion_time = None

    def can_fuse(self, p1: Pet, p2: Pet) -> bool:
        if frozenset((p1.element, p2.element)) in INCOMPATIBLE_PAIRS:
            return False
        if p1.level < MIN_FUSION_LEVEL or p2.level < MIN_FUSION_LEVEL:
            return False
        if p1.intimacy < MIN_INTIMACY or p2.intimacy < MIN_INTIMACY:
            return False
        return True

    def calculate_fused_stats(self, p1: Pet, p2: Pet) -> dict:
        atk = (p1.atk * MAIN_PET_RATIO + p2.atk * SUB_PET_RATIO) * STAT_DECAY
        return {"atk": atk}

    def get_fusion_skill(self, p1_element: str, p2_element: str) -> str:
        return FUSION_SKILLS.get(frozenset((p1_element, p2_element)), "fusion_attack")

    def get_fusion_duration(self) -> float:
        return FUSION_DURATION

    def get_form_roll(self, target_form: str) -> tuple[str, bool]:
        count = self.form_pity.get(target_form, 0)
        if count >= PITY_LIMIT:
            self.form_pity[target_form] = 0
            return target_form, True
        form = self.rng.choice(FORMS)
        if form == target_form:
            self.form_pity[target_form] = 0
            return form, True
        self.form_pity[target_form] = count + 1
        return form, False

    def fusion_failure_cost(self) -> dict:
        return {"material_cost": FAILURE_MATERIAL_RATIO}

    def get_fusion_cooldown(self) -> float:
        return FUSION_COOLDOWN

    def get_energy_cost(self, skill: str) -> float:
        return SKILL_ENERGY_COSTS.get(skill, DEFAULT_ENERGY_COST)

    def consume_energy(self, skill: str) -> bool:
        """放技能扣能量；能量耗尽返回False表示强制解除变身"""
        self.energy = max(0.0, self.energy - self.get_energy_cost(skill))
        return self.energy > 0

    def get_inherited_skills_limit(self) -> int:
        return INHERITED_SKILLS_LIMIT

    def inherit_skills(self, p1: Pet, p2: Pet) -> list:
        """最多继承3个技能，主宠优先"""
        merged = list(dict.fromkeys(p1.skills + p2.skills))
        return merged[:INHERITED_SKILLS_LIMIT]
