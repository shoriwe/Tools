require 'socket'
require 'timeout'
# Better recv function
def recv s
  buf = ''
  while true
    data = ''
    begin
      data = Timeout::timeout(0.1){
      s.recv(1024)
    }
    rescue
      if buf.length > 0
        buf
      else
        false
      end
    end

    if data.length < 1024
      return buf + data
    end
    buf += data
  end
end
# Create sockets
def create_socket host, port, mode='client'
  if mode == 'server'
    s = TCPServer.new(host, port)
  else
    address = Socket.pack_sockaddr_in(port, host)
    s = Socket.new(Socket::AF_INET, Socket::SOCK_STREAM)
    s.connect(address)
  end
  s
end

def tunnel_communication_handler local_socket, target_socket
  while true
    msg = recv(client)
    if msg
      target_socket.send msg, 0
    end
    response = recv(target_socket)
    if response
      client.send response, 0
    end
  end
end

def start
  local_socket = create_socket'192.168.0.19', 4444, 'server'
  target_socket = create_socket '127.0.0.1', 1235
  while true
    begin
      client = local_socket.accept
      puts client.port
      tunnel_communication_handler client, target_socket
    rescue
      nil
    end
  end
end
start