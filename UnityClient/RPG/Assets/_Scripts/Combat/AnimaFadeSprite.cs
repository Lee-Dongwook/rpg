using UnityEngine;

/// <summary>짧게 커지며 사라지는 전투 이펙트 스프라이트입니다.</summary>
public sealed class AnimaFadeSprite : MonoBehaviour
{
    [SerializeField] private float lifetime = .22f;
    [SerializeField] private float growth = 1.5f;
    [SerializeField] private bool faceCamera = true;

    private MeshRenderer spriteRenderer;
    private Material material;
    private Vector3 baseScale;
    private Color baseColor;
    private Quaternion roll = Quaternion.identity;
    private float age;

    public void Play(float life, float grow, bool billboard)
    {
        lifetime = life;
        growth = grow;
        faceCamera = billboard;
    }

    private void Awake()
    {
        spriteRenderer = GetComponentInChildren<MeshRenderer>();
        if (spriteRenderer == null) return;
        material = spriteRenderer.material;
        baseColor = material.GetColor("_UnlitColor");
        baseScale = spriteRenderer.transform.localScale;
        // 참격처럼 무작위로 기울인 이펙트는 빌보드 회전 위에 그 기울기를 덧입힙니다.
        roll = Quaternion.Euler(0f, 0f, spriteRenderer.transform.localEulerAngles.z);
    }

    private void LateUpdate()
    {
        if (spriteRenderer == null)
        {
            Destroy(gameObject);
            return;
        }

        age += Time.deltaTime;
        var t = Mathf.Clamp01(age / lifetime);

        if (faceCamera && Camera.main != null)
            spriteRenderer.transform.rotation = Camera.main.transform.rotation * roll;

        spriteRenderer.transform.localScale = baseScale * Mathf.Lerp(1f, growth, t);
        var color = baseColor;
        color.a = baseColor.a * (1f - t * t);
        material.SetColor("_UnlitColor", color);

        if (t >= 1f) Destroy(gameObject);
    }

    private void OnDestroy()
    {
        if (material != null) Destroy(material);
    }
}
