namespace GameShared.Models
{
    public class CharacterData
    {
        public string Id { get; set; }
        public string DisplayName { get; set; }
        public int Cost { get; set; }
        public string[] Traits { get; set; }
        public int Hp { get; set; }
        public int MaxHp { get; set; }
        public int AttackPower { get; set; }
        public float AttackSpeed { get; set; }
        public int Armor { get; set; }
        public int MagicResist { get; set; }
        public int Range { get; set; }
        public CharacterData(string id, int maxHp, int attackPower)
        {
            Id = id;
            DisplayName = id;
            MaxHp = maxHp;
            Hp = maxHp;
            AttackPower = attackPower;
            Traits = System.Array.Empty<string>();
        }

        public void ApplyDamage(int damage)
        {
            Hp = System.Math.Max(0, Hp - damage);
        }
    }
}
