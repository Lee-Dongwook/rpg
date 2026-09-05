using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class GameClientManager : MonoBehaviour
{
    private TcpClient client;
    private StreamReader reader;
    private StreamWriter writer;
    private bool isConnected = false;

    private async void Start()
    {
        await ConnectToServer("127.0.0.1", 7777);
    }

    public async Task ConnectToServer(string ip, int port)
    {
        try
        {
            client = new TcpClient();
            await client.ConnectAsync(ip, port);
            isConnected = true;
            Debug.Log("[Client] 서버 연결 성공!");

            NetworkStream stream = client.GetStream();
            reader = new StreamReader(stream, Encoding.UTF8);
            writer = new StreamWriter(stream, Encoding.UTF8) { AutoFlush = true };

            _ = ListenForServerPackets();
            await writer.WriteLineAsync("{\"type\":\"hello\",\"client\":\"unity\"}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[Client] 서버 연결 실패: {e.Message}");
        }
    }

    private async Task ListenForServerPackets()
    {
        try
        {
            while (isConnected)
            {
                string packetJson = await reader.ReadLineAsync();
                if (packetJson != null)
                {
                    HandlePacket(packetJson);
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[Client] 서버와의 연결 종료: {e.Message}");
        }
    }

    private void HandlePacket(string json)
    {
        Debug.Log($"[Client] 패킷 수신: {json}");

        // TODO: 여기서 패킷 종류를 분석(Deserialization)하고, 
        // 스킬 사용 신호라면 FioraEffectController를 호출하여 
        // 화려한 난무 VFX와 카메라 셰이크를 터뜨립니다!
    }

    public async void SendCommand(string commandMessage)
    {
        if (!isConnected || writer == null) return;
        await writer.WriteLineAsync(commandMessage);
    }
    private void OnDestroy()
    {
        isConnected = false;
        reader?.Dispose();
        writer?.Dispose();
        client?.Close();
    }
}
