using UnityEngine;

/// <summary>전장을 위에서 비스듬히 내려다보는 TFT식 아이소메트릭 전투 카메라입니다.</summary>
[ExecuteAlways]
public sealed class CandyTasteThirdPersonCamera : MonoBehaviour
{
    [SerializeField] private Transform followTarget;
    [SerializeField] private Vector3 cameraOffset = new(0f, 6.5f, -7.3f);
    [SerializeField] private Vector3 lookOffset = new(0f, .45f, .35f);
    [SerializeField] private float damping = 8f;

    public void SetTarget(Transform value)
    {
        followTarget = value;
        SnapToTarget(instant: true);
    }

    public void SetFraming(Vector3 offset, Vector3 look)
    {
        cameraOffset = offset;
        lookOffset = look;
    }

    private void LateUpdate() => SnapToTarget(instant: !Application.isPlaying);

    private void SnapToTarget(bool instant)
    {
        if (followTarget == null) return;

        var desired = followTarget.position + cameraOffset;
        transform.position = instant
            ? desired
            : Vector3.Lerp(transform.position, desired, 1f - Mathf.Exp(-damping * Time.deltaTime));
        transform.LookAt(followTarget.position + lookOffset);
    }
}
