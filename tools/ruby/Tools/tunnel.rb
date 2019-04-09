require 'socket'
require 'timeout'
require 'optparse'
# Better recv function
def recv s
  buf = ''
  while true
    data = ''
    begin
      data = Timeout::timeout(5){
      s.recv(1024)
    }
    # When all goes wrong
    rescue
      # if we got at least some of the data
      if buf.length > 0
        buf
      # We could not get any amount of data
      else
        false
      end
    end
    # If all goes well return the buffer
    if data.length < 1024
      return buf + data
    end
    # Increase the buffer
    buf += data
  end
end
# Create sockets
def create_socket host, port, mode='client'
  if mode == 'server'
    s = TCPServer.new(host, port.to_i)
    s.listen 1
  else
    address = Socket.pack_sockaddr_in(port.to_i, host)
    s = Socket.new(Socket::AF_INET, Socket::SOCK_STREAM)
    s.connect(address)
  end
  s
end

def tunnel_communication_handler client, local_socket
  # The welcome message
  welcome = recv(local_socket)
  if welcome # If  the server send a welcome message
    client.send welcome, 0
  end
  while true
    # Client of the target host recv first
    msg = recv(client)
    if msg
      local_socket.send msg, 0
    end
    response = recv(local_socket)
    if response
      client.send response, 0
    end
  end
end

# target_address is the one to be forwarded
# Local address is the one only this machine have access
def start target_address, local_address
  target_socket = create_socket *target_address, 'server'
  local_socket = create_socket *local_address
  while true
    begin # if the connection dies, repeat again
      client = target_socket.accept
      # Start the communication
      tunnel_communication_handler client, local_socket
    rescue
      nil
    end
  end
end
def main args=[]
  parser = OptionParser.new('Usage tunnel.rb [target-host] [target-port] [local-host] [local-port]')
  parser.on('-h', '--help') do
    puts parser
    puts
    puts "----------------------------Definitions---------------------------------"
    puts "target-host     Host to send the data\n"\
         "target-port     Port of the target-host\n"\
         "local-host      Host that typically only  can be access by this machine\n"\
         "local-port      Port of local-host"
    return
  end.parse!
  if args.length < 4
    args = ARGV
  end
  if args.nil?
    puts "Wrong number of arguments"
    return
  end
  target_address = args[0...2]
  local_address  = args[2...]
  start target_address, local_address
end
main