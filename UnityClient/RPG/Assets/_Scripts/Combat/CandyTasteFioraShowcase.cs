using UnityEngine;

/// <summary>
/// Scene 뷰에서 바로 확인할 수 있는 '사탕맛' 전장 프리뷰입니다.
/// 외부 캐릭터 아트 대신 코드로 만든 오리지널 결투가형 프록시를 사용합니다.
/// </summary>
[ExecuteAlways]
public sealed class CandyTasteFioraShowcase : MonoBehaviour
{
    private const string PreviewRootName = "__사탕맛 Scene Preview";
    private static readonly Color Board = new(.025f, .04f, .10f);
    private static readonly Color Gold = new(1f, .66f, .12f);
    private static readonly Color Hair = new(.18f, .78f, 1f);
    private static readonly Color Armor = new(.16f, .12f, .34f);
    private static readonly Color Accent = new(1f, .12f, .55f);
    private static readonly Color Blade = new(.45f, 1f, .95f);

    private void OnEnable()
    {
        if (!Application.isPlaying) BuildPreview();
    }

    private void Start() => BuildPreview();

    private void OnValidate()
    {
        if (!Application.isPlaying) BuildPreview();
    }

    private void BuildPreview()
    {
        RemoveLegacyPreviewObjects();

        // 이 스크립트는 Main Camera에 붙어 있습니다. 프리뷰를 카메라 자식으로 만들면
        // 카메라와 전장이 함께 이동하는 순환 참조가 생기므로 반드시 월드 루트에 둡니다.
        // GameObject.Find는 첫 번째 항목만 반환합니다. ExecuteAlways 재컴파일/Play 전환 중
        // 중복 루트가 생길 수 있으므로, 같은 이름의 모든 이전 프리뷰를 화면에서 즉시 숨깁니다.
        foreach (var sceneObject in FindObjectsByType<GameObject>(FindObjectsInactive.Exclude, FindObjectsSortMode.None))
        {
            if (sceneObject.name != PreviewRootName) continue;
            sceneObject.SetActive(false);
            DestroyObject(sceneObject);
        }

        var root = new GameObject(PreviewRootName);
        root.transform.position = Vector3.zero;

        BuildBoard(root.transform);
        var candy = BuildDuelist(root.transform, "사탕맛 · 5코스트", new Vector3(0f, 0f, -1.05f));
        var target = BuildTarget(root.transform, new Vector3(0f, 0f, 2.1f));
        BuildVitals(root.transform, target.transform.position);
        BuildAura(root.transform, candy.transform.position);
        ConfigureThirdPersonCamera(candy.transform);

        // 실전 난무는 Play 모드에서만 실행합니다. Edit 모드에서는 배치/구도를 유지합니다.
        if (Application.isPlaying)
        {
            var controller = candy.AddComponent<CandyTasteFioraController>();
            controller.SetTarget(target.transform);
        }
    }

    private static void RemoveLegacyPreviewObjects()
    {
        // 초기 도형 프리뷰는 월드 루트에 생성되어 씬에 남아 있을 수 있습니다.
        // 새 프리뷰의 자식은 건드리지 않고, 루트에 남은 이전 버전만 한 번 정리합니다.
        var legacyNames = new[]
        {
            "TFT 전투 보드", "사탕맛 (5코스트)", "사탕맛의 검", "훈련용 적",
            "정보 라벨", "사탕맛 - 2칸 치유 오라", "급소 타격"
        };

        foreach (var sceneObject in FindObjectsByType<GameObject>(FindObjectsInactive.Exclude, FindObjectsSortMode.None))
        {
            if (sceneObject.transform.parent != null) continue;
            foreach (var legacyName in legacyNames)
            {
                if (sceneObject.name != legacyName) continue;
                DestroyObject(sceneObject);
                break;
            }
        }
    }

    private static void BuildBoard(Transform parent)
    {
        var board = Primitive(parent, "전투 보드", PrimitiveType.Cylinder, Vector3.zero, new Vector3(5.6f, .12f, 4.2f), Board);
        board.transform.localPosition = new Vector3(0f, -.16f, 0f);
        for (var x = -2; x <= 2; x++)
        for (var z = -2; z <= 2; z++)
        {
            var hex = Primitive(parent, "전투 칸", PrimitiveType.Cylinder, new Vector3(x * 1.3f, -.02f, z * 1.25f), new Vector3(.58f, .018f, .58f), new Color(.08f, .16f, .28f));
            hex.transform.localRotation = Quaternion.Euler(0f, 30f, 0f);
        }
    }

    private static GameObject BuildDuelist(Transform parent, string name, Vector3 position)
    {
        var unit = new GameObject(name);
        unit.transform.SetParent(parent, false);
        unit.transform.localPosition = position;

        Primitive(unit.transform, "다리 L", PrimitiveType.Cylinder, new Vector3(-.18f, .38f, 0f), new Vector3(.18f, .45f, .18f), Armor);
        Primitive(unit.transform, "다리 R", PrimitiveType.Cylinder, new Vector3(.18f, .38f, 0f), new Vector3(.18f, .45f, .18f), Armor);
        Primitive(unit.transform, "갑옷 몸통", PrimitiveType.Capsule, new Vector3(0f, 1.03f, 0f), new Vector3(.48f, .72f, .34f), Armor);
        Primitive(unit.transform, "어깨 갑옷 L", PrimitiveType.Sphere, new Vector3(-.42f, 1.38f, 0f), new Vector3(.32f, .22f, .32f), Accent);
        Primitive(unit.transform, "어깨 갑옷 R", PrimitiveType.Sphere, new Vector3(.42f, 1.38f, 0f), new Vector3(.32f, .22f, .32f), Accent);
        Primitive(unit.transform, "얼굴", PrimitiveType.Sphere, new Vector3(0f, 1.72f, 0f), new Vector3(.34f, .38f, .30f), new Color(1f, .72f, .61f));
        Primitive(unit.transform, "푸른 머리", PrimitiveType.Sphere, new Vector3(0f, 1.94f, .02f), new Vector3(.39f, .20f, .34f), Hair);
        Primitive(unit.transform, "긴 머리", PrimitiveType.Capsule, new Vector3(.27f, 1.54f, .08f), new Vector3(.13f, .45f, .13f), Hair);
        Primitive(unit.transform, "망토", PrimitiveType.Cube, new Vector3(0f, 1.0f, .24f), new Vector3(.65f, .85f, .06f), new Color(.08f, .04f, .20f));

        var blade = Primitive(unit.transform, "빛나는 레이피어", PrimitiveType.Cube, new Vector3(.75f, 1.22f, 0f), new Vector3(.055f, .055f, 1.55f), Blade);
        blade.transform.localRotation = Quaternion.Euler(54f, 0f, -45f);
        Primitive(unit.transform, "검 손잡이", PrimitiveType.Cylinder, new Vector3(.41f, .89f, 0f), new Vector3(.11f, .28f, .11f), Gold);

        CreateWorldLabel(unit.transform, "사탕맛", new Vector3(0f, 2.45f, 0f), Gold, 44);
        CreateWorldLabel(unit.transform, "★★★★★  5 COST", new Vector3(0f, 2.18f, 0f), Color.white, 24);
        return unit;
    }

    private static GameObject BuildTarget(Transform parent, Vector3 position)
    {
        var target = new GameObject("훈련용 적");
        target.transform.SetParent(parent, false);
        target.transform.localPosition = position;
        Primitive(target.transform, "적 몸통", PrimitiveType.Capsule, new Vector3(0f, .75f, 0f), new Vector3(.42f, .7f, .38f), new Color(.28f, .12f, .42f));
        Primitive(target.transform, "적 머리", PrimitiveType.Sphere, new Vector3(0f, 1.48f, 0f), new Vector3(.28f, .28f, .28f), new Color(.62f, .32f, .68f));
        CreateWorldLabel(target.transform, "TARGET", new Vector3(0f, 2.0f, 0f), new Color(1f, .42f, .72f), 24);
        return target;
    }

    private static void BuildVitals(Transform parent, Vector3 targetPosition)
    {
        for (var index = 0; index < 6; index++)
        {
            var angle = index * 60f * Mathf.Deg2Rad;
            var point = targetPosition + new Vector3(Mathf.Cos(angle), .88f, Mathf.Sin(angle)) * .83f;
            Primitive(parent, "급소 " + (index + 1), PrimitiveType.Sphere, point, Vector3.one * .12f, Accent);
        }
    }

    private static void BuildAura(Transform parent, Vector3 position)
    {
        var aura = Primitive(parent, "2칸 치유 오라", PrimitiveType.Cylinder, position + Vector3.up * .01f, new Vector3(1.55f, .012f, 1.55f), new Color(.15f, .95f, .78f));
        aura.transform.localRotation = Quaternion.Euler(0f, 30f, 0f);
    }

    private static GameObject Primitive(Transform parent, string name, PrimitiveType type, Vector3 position, Vector3 scale, Color color)
    {
        var shape = GameObject.CreatePrimitive(type);
        shape.name = name;
        shape.transform.SetParent(parent, false);
        shape.transform.localPosition = position;
        shape.transform.localScale = scale;
        shape.GetComponent<Renderer>().material.color = color;
        var collider = shape.GetComponent<Collider>();
        if (collider != null) DestroyObject(collider);
        return shape;
    }

    private static void CreateWorldLabel(Transform parent, string content, Vector3 position, Color color, int size)
    {
        var label = new GameObject("라벨: " + content, typeof(TextMesh));
        label.transform.SetParent(parent, false);
        label.transform.localPosition = position;
        var text = label.GetComponent<TextMesh>();
        text.text = content;
        text.anchor = TextAnchor.MiddleCenter;
        text.alignment = TextAlignment.Center;
        text.characterSize = .07f;
        text.fontSize = size;
        text.color = color;
    }

    private static void ConfigureThirdPersonCamera(Transform target)
    {
        var camera = Camera.main;
        if (camera == null) return;
        var thirdPerson = camera.GetComponent<CandyTasteThirdPersonCamera>();
        if (thirdPerson == null) thirdPerson = camera.gameObject.AddComponent<CandyTasteThirdPersonCamera>();
        thirdPerson.SetTarget(target);
    }

    private static void DestroyObject(Object target)
    {
        if (Application.isPlaying) Destroy(target);
        else DestroyImmediate(target);
    }
}
