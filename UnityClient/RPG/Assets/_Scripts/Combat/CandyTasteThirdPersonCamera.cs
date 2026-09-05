using UnityEngine;

/// <summary>사탕맛 뒤쪽에서 적을 함께 바라보는 고정 3인칭 전투 카메라입니다.</summary>
[ExecuteAlways]
public sealed class CandyTasteThirdPersonCamera : MonoBehaviour
{
    [SerializeField] private Transform followTarget;
    [SerializeField] private Vector3 cameraOffset = new(0f, 2.25f, -5.6f);
    [SerializeField] private Vector3 lookOffset = new(0f, 1.15f, 2.4f);

    public void SetTarget(Transform value)
    {
        followTarget = value;
        SnapToTarget();
    }

    private void LateUpdate() => SnapToTarget();

    private void SnapToTarget()
    {
        if (followTarget == null) return;
        transform.position = followTarget.position + cameraOffset;
        transform.LookAt(followTarget.position + lookOffset);
    }
}
