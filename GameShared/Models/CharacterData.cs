namespace GameShared.Models
{
    public class CharacterData
    {
        public string Id { get; set; }
        public int Hp { get; set; }
        public int MaxHp { get; set; }
        public int AttackPower { get; set; }

        public CharacterData(string id, int maxHp, int attackPower)
        {
            Id = id;
            MaxHp = maxHp;
            Hp = maxHp; 
            AttackPower = attackPower;
        }

        public void ApplyDamage(int damage)
        {
            Hp = System.Math.Max(0, Hp - damage);
        }
    }
}
