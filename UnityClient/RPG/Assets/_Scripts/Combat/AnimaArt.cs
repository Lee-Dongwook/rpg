using UnityEngine;
using UnityEngine.Rendering.HighDefinition;

/// <summary>
/// Resources/AnimaSquad 아래의 핸드페인팅 아트를 HDRP 언릿 머티리얼과 스프라이트 쿼드로 바꿔 줍니다.
/// 아트에 조명이 이미 구워져 있으므로 씬 조명을 타지 않는 Unlit을 사용합니다.
/// </summary>
public static class AnimaArt
{
    public const string ResourceRoot = "AnimaSquad/";

    public enum Blend
    {
        /// <summary>알파 컷아웃 + 알파 블렌딩. 유닛/보드처럼 형태가 또렷한 아트용.</summary>
        Cutout,
        /// <summary>알파 블렌딩만. 반투명 그림자처럼 부드러운 아트용.</summary>
        Alpha,
        /// <summary>가산 합성. 발광 이펙트용.</summary>
        Additive,
    }

    public static Texture2D Texture(string fileName)
    {
        var texture = Resources.Load<Texture2D>(ResourceRoot + fileName);
        if (texture == null) Debug.LogWarning($"[AnimaArt] 텍스처를 찾을 수 없습니다: Resources/{ResourceRoot}{fileName}");
        return texture;
    }

    public static Material Material(Texture2D texture, Blend blend, Color tint)
    {
        var shader = Shader.Find("HDRP/Unlit");
        var material = new Material(shader)
        {
            name = "Anima " + (texture != null ? texture.name : "Untextured"),
            hideFlags = HideFlags.DontSave,
        };

        material.SetTexture("_UnlitColorMap", texture);
        material.SetColor("_UnlitColor", tint);
        material.SetFloat("_DoubleSidedEnable", 1f);
        material.SetFloat("_CullMode", (float)UnityEngine.Rendering.CullMode.Off);
        // 0 = Alpha, 1 = Additive (HDRP BlendMode)
        material.SetFloat("_BlendMode", blend == Blend.Additive ? 1f : 0f);
        // 컷아웃 스프라이트는 뎁스를 써야 서로 겹칠 때 정렬이 안정적입니다.
        material.SetFloat("_TransparentZWrite", blend == Blend.Cutout ? 1f : 0f);

        HDMaterial.SetSurfaceType(material, transparent: true);
        HDMaterial.SetAlphaClipping(material, blend == Blend.Cutout);
        HDMaterial.SetAlphaCutoff(material, .04f);
        HDMaterial.SetRenderingPass(material, HDMaterial.RenderingPass.Default);
        HDMaterial.ValidateMaterial(material);
        return material;
    }

    /// <summary>텍스처 비율을 유지한 쿼드를 만듭니다. 높이(worldHeight)만 지정하면 폭은 자동입니다.</summary>
    public static GameObject Quad(Transform parent, string name, Texture2D texture, float worldHeight,
                                  Blend blend = Blend.Cutout, Color? tint = null)
    {
        var quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
        quad.name = name;
        quad.transform.SetParent(parent, false);

        var collider = quad.GetComponent<Collider>();
        if (collider != null) Destroy(collider);

        var aspect = texture != null && texture.height > 0 ? (float)texture.width / texture.height : 1f;
        quad.transform.localScale = new Vector3(worldHeight * aspect, worldHeight, 1f);

        var renderer = quad.GetComponent<MeshRenderer>();
        renderer.sharedMaterial = Material(texture, blend, tint ?? Color.white);
        renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        renderer.receiveShadows = false;
        return quad;
    }

    /// <summary>바닥에 눕힌 쿼드(보드, 헥사 타일, 오라 등).</summary>
    public static GameObject GroundQuad(Transform parent, string name, Texture2D texture, float worldSize,
                                        Blend blend = Blend.Cutout, Color? tint = null)
    {
        var quad = Quad(parent, name, texture, worldSize, blend, tint);
        quad.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
        return quad;
    }

    /// <summary>발밑을 기준점으로 카메라를 향해 서 있는 스프라이트를 만듭니다.</summary>
    public static GameObject Billboard(Transform parent, string name, Texture2D texture, float worldHeight,
                                       Vector3 groundPosition, Blend blend = Blend.Cutout, float footOffset = 0f)
    {
        var pivot = new GameObject(name);
        pivot.transform.SetParent(parent, false);
        pivot.transform.localPosition = groundPosition;

        var quad = Quad(pivot.transform, name + " 스프라이트", texture, worldHeight, blend);
        var billboard = pivot.AddComponent<AnimaBillboard>();
        billboard.Configure(quad.transform, worldHeight * .5f + footOffset);
        return pivot;
    }

    private static void Destroy(Object target)
    {
        if (Application.isPlaying) Object.Destroy(target);
        else Object.DestroyImmediate(target);
    }
}
