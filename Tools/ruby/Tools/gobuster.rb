require 'socket'
require 'net/http'
require 'optparse'
# Strip each word of the wordlist
def depurate_wordlist(wordlist)
  buffer = []
  wordlist.each {|word|
    buffer << word.strip
  }
  buffer
end
# Gobuster Handler
class GoBuster
  def initialize
    # Wordlist is going to be stored here as an array
    @wordlist = nil
    # The maximum number of threads that can be up at the same time
    @max_threads = nil
    # The target url that is going to be listed
    @target_url = nil
    # Status codes that you  wan to check
    @status_codes = nil
    # User-Agent for the request
    @user_agent = nil
    # Cookies for the request
    @cookies = nil

    # File formats to be processed
    @file_extensions = ['']

    # Memory for control the maximum number of threads active at the same time
    @active_threads = 0
  end

  def set_cookies(cookies)
    @cookies = cookies
  end
  # Set the user agent for the request
  def set_useragent(user_agent)
    @user_agent = user_agent
  end
  # Set the extension to be added to the listing
  def set_extensions(extensions)
    extensions.split(',').each do |x|
      @file_extensions << ".#{x}"
    end
  end
  # Url to be processed
  def set_url(url)
    @target_url = url
  end
  # Set the max number of active threads at the same timed
  def set_threads(n)
    @max_threads = n
  end

  # Setup all wanted status codes
  def set_statuscodes(codes)
    @status_codes = codes.split(',')
  end
  # Setup wordlist to be used for thedirectory listing
  def set_wordlist(filename)
    filehandler = File.open(filename, 'r')
    # Depurate thewordlist  striping all elements
    @wordlist = depurate_wordlist filehandler.readlines
    # Close the file
    filehandler.close
  end

  # Request handler
  def request_handler(directory, extension)
    @active_threads += 1
    begin
      # Merge the base url and the directory from the wordlist
      url = URI("#{@target_url}/#{directory}#{extension}")
      # Get the status code of the url
      code = Net::HTTP.get_response(url).code
      # Check if the response code is in the wanted codes
      if @status_codes.include? code
        puts "/#{directory}#{extension} (Code #{code})"
      end
    rescue
      nil
    end
      @active_threads -= 1
  end

  # Start the gobuster
  def start
    @wordlist.each do |word|
      # format each file format with each directory them check it
      @file_extensions.each do |x|
        # Wait until active threads are less than the maximum limit
        while @active_threads >= @max_threads
          nil
        end
        # Start a thread
        Thread.new {request_handler(word, x)}
        sleep(0.00000000001) # Wairt for Thread initialization
      end
    end
    while @active_threads > 0
      nil
    end
  end

end

# Options for  implement
# -c cookies for the requests
# -a set user agent

def main(args = nil)
  # Creation of options
  args = {:set_url => nil, :set_wordlist => nil, :set_threads => 10, :set_extensions => '', :set_statuscodes => '200,204,301,302,307,403', :set_useragent => 'Mozilla/5.0 (Windows NT 5.1; rv:9.0.1) Gecko/20100101 Firefox/9.0.1', :set_cookies => ''}
  opts = OptionParser.new
  opts.banner = "Gobuster ruby clone"
  opts.on("-u", "--url URL", "Target url to be listed") do |url|
    args[:set_url] = url
  end
  opts.on('-w', '--wordlist FILENAME', 'Set the file with the listing you want to try') do |file|
    args[:set_wordlist] = file
  end
  opts.on('-t', '--threads N_THREADS', "The max number of  active threads at the same time") do |n|
    args[:set_threads] = n.to_i
  end
  opts.on('-x', '--extensions EXT1,EXT2,EXT3', 'Set extension to permute with each directory in the wordlist') do |fmats|
    args[:set_extensions] = fmats
  end
  opts.on('-s', '--status-codes CODES', 'Status codes that you want to use as reference') do |codes|
    args[:set_statuscodes] = codes
  end
  # Not implemented yet
  # opts.on('-c', '--cookies', 'Cookies for the request') do |cookies|
  #   args[:set_cookies] = cookies
  # end
  # opts.on('-a', '--user-agent', "User Agent for the request") do |user_agent|
  #   args[:set_useragent] = user_agent
  # end
  opts.on('-h', '--help', 'Prints this help') do
    puts opts
  end.parse!

  begin
    g = GoBuster.new
    # Modular configuration
    args.each_key.each do |key|
      g.send key, args[key]
    end
    g.start
  rescue
    puts opts
  end
end

# Run the script
main