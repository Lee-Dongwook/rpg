using System.Collections;
using UnityEngine;

/// <summary>
/// Set 17 5코스트 피오라형 '사탕맛'의 전투 시연 컨트롤러입니다.
/// 매 2회 공격의 급소 돌진과 70마나 시 6개 급소 난무를 시각화하며,
/// 타격/치유 연출은 Resources/AnimaSquad 의 이펙트 스프라이트를 사용합니다.
/// </summary>
public sealed class CandyTasteFioraController : MonoBehaviour
{
    public const string UnitName = "사탕맛";
    public const int Cost = 5;
    public const int MaxHealth = 1200;
    public const int AttackDamage = 80;
    public const int MaxMana = 70;
    public const float AttackSpeed = .9f;
    public const int Armor = 65;
    public const int MagicResist = 65;
    public const int Range = 1;
    public static readonly string[] Traits = { "애니마", "신성한 결투가", "약탈자" };

    [SerializeField] private Transform target;
    [SerializeField] private float demoRepeatSeconds = 4.5f;

    // 보드 크기(가로 5칸, 세로 5칸)에 맞춘 이동 가능 범위입니다.
    // 카메라가 캐릭터를 따라가더라도 전장 밖으로 벗어나지 않습니다.
    [SerializeField] private Vector2 fieldHalfExtents = new(2.3f, 2f);

    private Vector3 homePosition;
    private int attacks;
    private bool casting;

    private void Start()
    {
        homePosition = transform.position;
        StartCoroutine(DemoLoop());
    }

    public void ReceiveSkillSignal()
    {
        if (!casting) StartCoroutine(PerfectBladework());
    }

    private IEnumerator DemoLoop()
    {
        yield return new WaitForSeconds(1f);
        while (enabled)
        {
            yield return BasicAttack();
            yield return BasicAttack();
            yield return new WaitForSeconds(.35f);
            yield return PerfectBladework();
            yield return new WaitForSeconds(demoRepeatSeconds);
        }
    }

    private IEnumerator BasicAttack()
    {
        attacks++;
        if (attacks % 2 == 0) yield return DashToVital(0);
        else yield return new WaitForSeconds(1f / AttackSpeed);
    }

    private IEnumerator PerfectBladework()
    {
        if (casting || target == null) yield break;
        casting = true;
        for (var i = 0; i < 6; i++)
        {
            yield return DashToVital(i);
            yield return new WaitForSeconds(.06f);
        }
        transform.position = homePosition;
        StartCoroutine(HealingAura());
        casting = false;
    }

    private IEnumerator DashToVital(int index)
    {
        if (target == null) yield break;
        var direction = Quaternion.Euler(0f, index * 60f, 0f) * Vector3.forward;
        var destination = ClampToField(target.position + direction * 1.05f);
        var start = transform.position;
        const float duration = .12f;
        for (var time = 0f; time < duration; time += Time.deltaTime)
        {
            transform.position = ClampToField(Vector3.Lerp(start, destination, time / duration));
            yield return null;
        }
        transform.position = destination;
        SpawnStrike(destination, direction);
    }

    private IEnumerator HealingAura()
    {
        var aura = AnimaArt.GroundQuad(null, "사탕맛 - 2칸 치유 오라", AnimaArt.Texture("aura_ring"),
                                       4f, AnimaArt.Blend.Additive);
        aura.transform.position = homePosition + Vector3.up * .03f;
        aura.AddComponent<AnimaFadeSprite>().Play(5f, 1.06f, billboard: false);
        yield return new WaitForSeconds(5.1f);
    }

    /// <summary>급소를 찌른 순간의 참격과 타격 스파크를 띄웁니다.</summary>
    private static void SpawnStrike(Vector3 position, Vector3 direction)
    {
        var center = position + Vector3.up * .95f - direction * .35f;

        var slash = AnimaArt.Quad(null, "급소 참격", AnimaArt.Texture("slash_fx"), 1.5f,
                                  AnimaArt.Blend.Additive);
        slash.transform.position = center;
        slash.transform.localRotation = Quaternion.Euler(0f, 0f, Random.Range(0f, 360f));
        slash.AddComponent<AnimaFadeSprite>().Play(.2f, 1.5f, billboard: true);

        var spark = AnimaArt.Quad(null, "타격 스파크", AnimaArt.Texture("hit_spark"), .8f,
                                  AnimaArt.Blend.Additive);
        spark.transform.position = center;
        spark.AddComponent<AnimaFadeSprite>().Play(.16f, 1.9f, billboard: true);
    }

    public void SetTarget(Transform value) => target = value;

    private Vector3 ClampToField(Vector3 position)
    {
        position.x = Mathf.Clamp(position.x, -fieldHalfExtents.x, fieldHalfExtents.x);
        position.z = Mathf.Clamp(position.z, -fieldHalfExtents.y, fieldHalfExtents.y);
        return position;
    }
}
