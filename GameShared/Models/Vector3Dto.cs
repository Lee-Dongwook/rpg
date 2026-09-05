namespace GameShared.Models
{
    public struct Vector3Dto
    {
        public float X { get; set; }
        public float Y { get; set; }
        public float Z { get; set; }

        public Vector3Dto(float x, float y, float z)
        {
            X = x;
            Y = y;
            Z = z;
        }
    }
}
