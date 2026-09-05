using System.Net;
using System.Net.Sockets;
using System.Text;

const int port = 7777;
var listener = new TcpListener(IPAddress.Any, port);
listener.Start();

Console.WriteLine($"[Server] TCP 서버 시작: 0.0.0.0:{port}");
Console.WriteLine("[Server] 종료하려면 Ctrl+C를 누르세요.");

while (true)
{
    TcpClient client = await listener.AcceptTcpClientAsync();
    _ = HandleClientAsync(client);
}

static async Task HandleClientAsync(TcpClient client)
{
    var remoteEndPoint = client.Client.RemoteEndPoint;
    Console.WriteLine($"[Server] 클라이언트 접속: {remoteEndPoint}");

    using (client)
    using (NetworkStream stream = client.GetStream())
    using (var reader = new StreamReader(stream, Encoding.UTF8))
    using (var writer = new StreamWriter(stream, Encoding.UTF8) { AutoFlush = true })
    {
        await writer.WriteLineAsync("{\"type\":\"connected\",\"message\":\"서버 연결 완료\"}");

        try
        {
            string? message;
            while ((message = await reader.ReadLineAsync()) is not null)
            {
                Console.WriteLine($"[Server] 수신: {message}");
                await writer.WriteLineAsync(message);
            }
        }
        catch (IOException exception)
        {
            Console.WriteLine($"[Server] 연결 종료: {exception.Message}");
        }
    }

    Console.WriteLine($"[Server] 클라이언트 연결 해제: {remoteEndPoint}");
}
