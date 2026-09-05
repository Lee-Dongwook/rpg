using UnityEngine;

/// <summary>빈 HDRP 씬에서도 사탕맛 전투 프리뷰를 자동으로 구성합니다.</summary>
public sealed class CandyTasteFioraShowcase : MonoBehaviour
{
    private void Awake()
    {
        BuildArena();
    }

    private static void BuildArena()
    {
        var floor = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        floor.name = "TFT 전투 보드";
        floor.transform.position = Vector3.zero;
        floor.transform.localScale = new Vector3(6.5f, .15f, 6.5f);
        floor.GetComponent<Renderer>().material.color = new Color(.045f, .06f, .14f);

        var candy = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        candy.name = "사탕맛 (5코스트)";
        candy.transform.position = new Vector3(-1.5f, .7f, 0f);
        candy.GetComponent<Renderer>().material.color = new Color(.92f, .23f, .57f);
        var controller = candy.AddComponent<CandyTasteFioraController>();

        var blade = GameObject.CreatePrimitive(PrimitiveType.Cube);
        blade.name = "사탕맛의 검";
        blade.transform.SetParent(candy.transform, false);
        blade.transform.localPosition = new Vector3(.46f, .42f, .05f);
        blade.transform.localScale = new Vector3(.08f, .08f, 1.25f);
        blade.transform.localRotation = Quaternion.Euler(45f, 0f, 0f);
        blade.GetComponent<Renderer>().material.color = new Color(.5f, .92f, 1f);

        var dummy = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        dummy.name = "훈련용 적";
        dummy.transform.position = new Vector3(1.4f, .7f, 0f);
        dummy.GetComponent<Renderer>().material.color = new Color(.32f, .27f, .55f);
        controller.SetTarget(dummy.transform);

        CreateLabel("사탕맛", new Vector3(-1.5f, 2.25f, 0f), Color.white, 38);
        CreateLabel("★★★★★  5코스트\n애니마 · 신성한 결투가 · 약탈자\n1200 HP | 80 AD | 0 / 70 마나", new Vector3(-1.5f, 1.72f, 0f), new Color(1f, .82f, .25f), 18);
        CreateLabel("완벽한 검술\n6개 급소 난무 → 2칸 치유 오라", new Vector3(1.4f, 2.1f, 0f), new Color(.35f, 1f, .9f), 18);
    }

    private static void CreateLabel(string value, Vector3 position, Color color, int size)
    {
        var label = new GameObject("정보 라벨");
        label.transform.position = position;
        label.transform.rotation = Quaternion.Euler(25f, 0f, 0f);
        var text = label.AddComponent<TextMesh>();
        text.text = value;
        text.anchor = TextAnchor.MiddleCenter;
        text.alignment = TextAlignment.Center;
        text.characterSize = .075f;
        text.fontSize = size;
        text.color = color;
    }
}
