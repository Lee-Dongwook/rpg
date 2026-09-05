using System.Collections;
using UnityEngine;

/// <summary>
/// Set 17 5코스트 피오라형 '사탕맛'의 전투 시연 컨트롤러입니다.
/// 매 2회 공격의 급소 돌진과 70마나 시 6개 급소 난무를 시각화합니다.
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
        var destination = target.position + direction * 1.05f;
        var start = transform.position;
        const float duration = .12f;
        for (var time = 0f; time < duration; time += Time.deltaTime)
        {
            transform.position = Vector3.Lerp(start, destination, time / duration);
            yield return null;
        }
        transform.position = destination;
        SpawnRing(destination, new Color(1f, .31f, .67f), .36f, .16f);
    }

    private IEnumerator HealingAura()
    {
        var aura = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        aura.name = "사탕맛 - 2칸 치유 오라";
        aura.transform.position = homePosition + Vector3.down * .45f;
        aura.transform.localScale = new Vector3(4f, .025f, 4f);
        aura.GetComponent<Renderer>().material.color = new Color(.26f, .97f, .84f, .5f);
        Destroy(aura.GetComponent<Collider>());
        yield return new WaitForSeconds(5f);
        Destroy(aura);
    }

    private static void SpawnRing(Vector3 position, Color color, float size, float lifetime)
    {
        var ring = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        ring.name = "급소 타격";
        ring.transform.position = position + Vector3.up * .5f;
        ring.transform.localScale = Vector3.one * size;
        ring.GetComponent<Renderer>().material.color = color;
        Destroy(ring.GetComponent<Collider>());
        Destroy(ring, lifetime);
    }

    public void SetTarget(Transform value) => target = value;
}
