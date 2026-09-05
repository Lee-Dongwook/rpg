using UnityEngine;

/// <summary>
/// 스프라이트를 항상 카메라와 같은 방향으로 세워 둡니다.
/// 아트가 아이소메트릭 3/4 탑다운 시점으로 그려져 있어 카메라 정렬 빌보드가 가장 자연스럽습니다.
/// </summary>
[ExecuteAlways]
public sealed class AnimaBillboard : MonoBehaviour
{
    [SerializeField] private Transform sprite;
    [SerializeField] private float liftAlongCameraUp = .5f;

    public void Configure(Transform spriteTransform, float lift)
    {
        sprite = spriteTransform;
        liftAlongCameraUp = lift;
        Align();
    }

    private void LateUpdate() => Align();

    private void Align()
    {
        if (sprite == null) return;
        var camera = Camera.main;
        if (camera == null) return;

        var rotation = camera.transform.rotation;
        sprite.rotation = rotation;
        // 접지점(pivot)은 그대로 두고 스프라이트만 카메라 업 방향으로 들어 올려 발이 바닥에 붙게 합니다.
        sprite.position = transform.position + rotation * Vector3.up * liftAlongCameraUp;
    }
}
