namespace GameShared.Models
{
    public class SkillData
    {
        public string SkillId { get; set; }
        public string SkillName { get; set; }
        public int ManaCost { get; set; }
        public float Cooldown { get; set; }
        public int BaseDamage { get; set; }
        public SkillData(string skillId, string skillName, int manaCost, float cooldown, int baseDamage)
        {
            SkillId = skillId;
            SkillName = skillName;
            ManaCost = manaCost;
            Cooldown = cooldown;
            BaseDamage = baseDamage;
        }
    }
}
