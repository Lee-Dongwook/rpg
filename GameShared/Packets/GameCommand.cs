namespace GameShared.Packets
{
    using GameShared.Models;

    public enum CommandType
    {
        Move,
        UseSkill
    }

    public class GameCommand
    {
        public CommandType Type { get; set; }
        public string CharacterId { get; set; }
        public Vector3Dto TargetPosition { get; set; }
        public string SkillId { get; set; }

        public GameCommand(CommandType type, string characterId)
        {
            Type = type;
            CharacterId = characterId;
        }
    }
}
