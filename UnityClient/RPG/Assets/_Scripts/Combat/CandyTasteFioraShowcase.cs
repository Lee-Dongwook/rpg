using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;

/// <summary>
/// Scene 뷰에서 바로 확인할 수 있는 애니마 스쿼드 전장 프리뷰입니다.
/// 도형 프리미티브 대신 Resources/AnimaSquad 의 핸드페인팅 아트를 스프라이트로 배치합니다.
/// </summary>
[ExecuteAlways]
public sealed class CandyTasteFioraShowcase : MonoBehaviour
{
    private const string PreviewRootName = "__애니마 스쿼드 전장";
    private const string VolumeName = "__애니마 포스트 프로세싱";

    [Header("전장")]
    [SerializeField] private float boardSize = 9.4f;
    [SerializeField] private int columns = 5;
    [SerializeField] private int rows = 5;
    [SerializeField] private float hexSize = 1.62f;

    [Header("유닛")]
    [SerializeField] private float fioraHeight = 2.75f;
    [SerializeField] private float targetHeight = 2.15f;
    [SerializeField] private Vector3 fioraStand = new(-.64f, 0f, -1.35f);
    [SerializeField] private Vector3 targetStand = new(.64f, 0f, 2.05f);

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
        foreach (var sceneObject in FindObjectsByType<GameObject>(FindObjectsInactive.Exclude, FindObjectsSortMode.None))
        {
            if (sceneObject.name != PreviewRootName) continue;
            sceneObject.SetActive(false);
            DestroyPreviewObject(sceneObject);
        }

        var root = new GameObject(PreviewRootName);
        root.transform.position = Vector3.zero;

        BuildBoard(root.transform);
        var fiora = BuildUnit(root.transform, "사탕맛 (애니마 스쿼드 피오라)", "unit_fiora",
                              fioraStand, fioraHeight, 1.55f);
        var target = BuildUnit(root.transform, "훈련용 표적", "unit_target",
                               targetStand, targetHeight, 1.2f);
        BuildStatusBar(fiora.transform, fioraHeight);
        ConfigureCamera(root.transform);
        ConfigurePostProcessing();

        // 실전 난무는 Play 모드에서만 실행합니다. Edit 모드에서는 배치/구도를 유지합니다.
        if (Application.isPlaying)
        {
            var controller = fiora.AddComponent<CandyTasteFioraController>();
            controller.SetTarget(target.transform);
        }
    }

    private static void RemoveLegacyPreviewObjects()
    {
        // 이전 도형 프리뷰가 월드 루트에 남아 있을 수 있어 한 번 정리합니다.
        var legacyNames = new[]
        {
            "__사탕맛 Scene Preview", "TFT 전투 보드", "사탕맛 (5코스트)", "사탕맛의 검",
            "훈련용 적", "정보 라벨", "사탕맛 - 2칸 치유 오라", "급소 타격",
        };

        foreach (var sceneObject in FindObjectsByType<GameObject>(FindObjectsInactive.Exclude, FindObjectsSortMode.None))
        {
            if (sceneObject.transform.parent != null) continue;
            foreach (var legacyName in legacyNames)
            {
                if (sceneObject.name != legacyName) continue;
                DestroyPreviewObject(sceneObject);
                break;
            }
        }
    }

    private void BuildBoard(Transform parent)
    {
        var board = new GameObject("전장 보드");
        board.transform.SetParent(parent, false);

        AnimaArt.GroundQuad(board.transform, "보드 바닥", AnimaArt.Texture("board_arena"), boardSize);

        var tile = AnimaArt.Texture("hex_tile");
        var activeTile = AnimaArt.Texture("hex_tile_active");

        // 포인티탑 헥사 격자: 가로 간격은 폭, 세로 간격은 높이의 3/4 만큼입니다.
        var spacingX = hexSize * .797f;
        var spacingZ = hexSize * .69f;
        var originX = -(columns - 1) * spacingX * .5f;
        var originZ = -(rows - 1) * spacingZ * .5f;

        for (var row = 0; row < rows; row++)
        for (var column = 0; column < columns; column++)
        {
            var offset = row % 2 == 0 ? 0f : spacingX * .5f;
            var position = new Vector3(originX + column * spacingX + offset - spacingX * .25f,
                                       .012f + row * .0006f,
                                       originZ + row * spacingZ);
            var isCenter = row == rows / 2 && column == columns / 2;
            var hex = AnimaArt.GroundQuad(board.transform, $"헥사 {row}-{column}",
                                          isCenter ? activeTile : tile, hexSize, AnimaArt.Blend.Alpha);
            hex.transform.localPosition = position;
        }
    }

    private GameObject BuildUnit(Transform parent, string name, string textureName,
                                 Vector3 stand, float height, float shadowSize)
    {
        var shadow = AnimaArt.GroundQuad(parent, name + " 그림자", AnimaArt.Texture("ground_shadow"),
                                         shadowSize, AnimaArt.Blend.Alpha);
        shadow.transform.localPosition = stand + Vector3.up * .05f;

        var unit = AnimaArt.Billboard(parent, name, AnimaArt.Texture(textureName), height, stand);
        // 그림자를 유닛의 자식으로 붙여 이동 시 함께 따라가게 합니다.
        shadow.transform.SetParent(unit.transform, true);
        return unit;
    }

    private static void BuildStatusBar(Transform unit, float unitHeight)
    {
        var pivot = new GameObject("유닛 상태 바");
        pivot.transform.SetParent(unit, false);
        var bar = AnimaArt.Quad(pivot.transform, "상태 바 스프라이트", AnimaArt.Texture("unit_bar"),
                                .38f, AnimaArt.Blend.Alpha);
        pivot.AddComponent<AnimaBillboard>().Configure(bar.transform, unitHeight + .42f);
    }

    private void ConfigureCamera(Transform boardRoot)
    {
        var camera = Camera.main;
        if (camera == null) return;

        var view = camera.GetComponent<CandyTasteThirdPersonCamera>();
        if (view == null) view = camera.gameObject.AddComponent<CandyTasteThirdPersonCamera>();
        // TFT 전장처럼 위에서 비스듬히 내려다보는 아이소메트릭 구도입니다.
        view.SetFraming(new Vector3(0f, 6.5f, -7.3f), new Vector3(0f, .45f, .35f));
        view.SetTarget(boardRoot);
    }

    private static void ConfigurePostProcessing()
    {
        foreach (var sceneObject in FindObjectsByType<GameObject>(FindObjectsInactive.Exclude, FindObjectsSortMode.None))
        {
            if (sceneObject.name == VolumeName) DestroyPreviewObject(sceneObject);
        }

        var host = new GameObject(VolumeName);
        var volume = host.AddComponent<Volume>();
        volume.isGlobal = true;
        volume.priority = 50f;

        var profile = ScriptableObject.CreateInstance<VolumeProfile>();
        profile.hideFlags = HideFlags.DontSave;

        var bloom = profile.Add<Bloom>(true);
        bloom.intensity.Override(.28f);
        bloom.scatter.Override(.72f);

        var vignette = profile.Add<Vignette>(true);
        vignette.intensity.Override(.34f);
        vignette.smoothness.Override(.5f);

        var grading = profile.Add<ColorAdjustments>(true);
        grading.saturation.Override(10f);
        grading.contrast.Override(8f);

        var tonemapping = profile.Add<Tonemapping>(true);
        tonemapping.mode.Override(TonemappingMode.ACES);

        volume.sharedProfile = profile;
    }

    private static void DestroyPreviewObject(Object target)
    {
        if (Application.isPlaying) Destroy(target);
        else DestroyImmediate(target);
    }
}
