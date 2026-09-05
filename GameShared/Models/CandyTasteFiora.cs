namespace GameShared.Models
{
    /// <summary>
    /// TFT Set 17 Fiora의 공개 유닛 수치를 기반으로 만든 프로젝트 전용 유닛 정의입니다.
    /// 이름만 '사탕맛'으로 바꾸고 비용, 특성, 전투 역할 및 스킬 구조를 유지합니다.
    /// </summary>
    public static class CandyTasteFiora
    {
        public const string Id = "candy-taste";
        public const string DisplayName = "사탕맛";
        public const int Cost = 5;
        public const int MaxHealth = 1200;
        public const int AttackDamage = 80;
        public const float AttackSpeed = 0.9f;
        public const int Armor = 65;
        public const int MagicResist = 65;
        public const int Range = 1;
        public const int MaxMana = 70;

        public static readonly string[] Traits = { "애니마", "신성한 결투가", "약탈자" };

        public static CharacterData CreateCharacter()
        {
            return new CharacterData(Id, MaxHealth, AttackDamage)
            {
                DisplayName = DisplayName,
                Cost = Cost,
                Traits = Traits,
                AttackSpeed = AttackSpeed,
                Armor = Armor,
                MagicResist = MagicResist,
                Range = Range
            };
        }

        public static SkillData CreateSkill() => new(
            "perfect-bladework",
            "완벽한 검술",
            MaxMana,
            0f,
            0);
    }
}
